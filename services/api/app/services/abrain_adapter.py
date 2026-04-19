"""ABrain Adapter Orchestrator V1.

Bringt die drei Bausteine zusammen:
- `abrain_context.build_adapter_context` fuer die LabOS-Sicht
- `abrain_actions.get_catalog` fuer die statische Tool-Surface
- `abrain_client` fuer optionale HTTP-Aufrufe gegen externes ABrain

Die Governance-Grenze bleibt LabOS: Jeder vorgeschlagene Action wird hier
gegen den statischen Katalog aufgeloest. Externe Entscheidungen werden in
`ABrainAdapterRecommendedAction` normalisiert, aber niemals hier direkt
ausgefuehrt.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlmodel import Session

from ..config import settings
from ..models import _utcnow
from ..schemas import (
    ABrainActionDescriptor,
    ABrainActionRiskLevel,
    ABrainAdapterContextRead,
    ABrainAdapterQueryRequest,
    ABrainAdapterRecommendedAction,
    ABrainAdapterResponse,
    ABrainContextSection,
    ABrainStatusRead,
)
from . import abrain_actions, abrain_client, abrain_context

_CONTRACT_VERSION = 'v1'


def get_status() -> ABrainStatusRead:
    mode_value = abrain_client.mode()
    if not abrain_client.is_enabled() or settings.abrain_use_stub or mode_value == 'local':
        return ABrainStatusRead(
            connected=False,
            mode='local',
            base_url=settings.abrain_base_url,
            timeout_seconds=settings.abrain_timeout_seconds,
            fallback_available=settings.abrain_use_local_fallback,
            note='ABrain-Adapter laeuft im lokalen Modus (Stub oder deaktiviert).',
        )
    probe = abrain_client.ping()
    if probe.success:
        return ABrainStatusRead(
            connected=True,
            mode='external',
            base_url=settings.abrain_base_url,
            timeout_seconds=settings.abrain_timeout_seconds,
            fallback_available=settings.abrain_use_local_fallback,
            note='Externes ABrain erreichbar. LabOS sendet Kontext an /query.',
        )
    return ABrainStatusRead(
        connected=False,
        mode='external',
        base_url=settings.abrain_base_url,
        timeout_seconds=settings.abrain_timeout_seconds,
        fallback_available=settings.abrain_use_local_fallback,
        note='Externes ABrain aktuell nicht erreichbar. Fallback auf lokale Logik verfuegbar.',
    )


def build_context(
    session: Session,
    *,
    include_sections: list[ABrainContextSection] | None = None,
) -> ABrainAdapterContextRead:
    return abrain_context.build_adapter_context(
        session,
        include_sections=include_sections,
        mode=_current_mode(),
        fallback_used=False,
    )


def query_adapter(
    session: Session,
    payload: ABrainAdapterQueryRequest,
) -> ABrainAdapterResponse:
    context = abrain_context.build_adapter_context(
        session,
        include_sections=payload.include_context_sections,
        mode=_current_mode(),
    )
    external_result = _try_external(context, payload)
    response = external_result if external_result is not None else _build_local_response(
        context,
        payload,
        fallback_used=abrain_client.is_enabled() and not settings.abrain_use_stub,
    )
    _record_trace(session, context, payload, response)
    return response


def _record_trace(
    session: Session,
    context: ABrainAdapterContextRead,
    payload: ABrainAdapterQueryRequest,
    response: ABrainAdapterResponse,
) -> None:
    if not response.trace_id:
        return
    from . import traces as traces_service  # local import to avoid cycles
    snapshot = traces_service.build_snapshot_from_adapter(context, response)
    trace_source = 'abrain' if response.mode == 'external' else 'local'
    traces_service.ensure_trace(
        session,
        trace_id=response.trace_id,
        source=trace_source,
        root_query=payload.question,
        summary=response.summary,
        context_snapshot=snapshot,
    )


def _try_external(
    context: ABrainAdapterContextRead,
    payload: ABrainAdapterQueryRequest,
) -> ABrainAdapterResponse | None:
    if not abrain_client.is_enabled() or settings.abrain_use_stub or abrain_client.mode() == 'local':
        return None
    request_payload = {
        'question': payload.question,
        'preset': payload.preset.value if payload.preset is not None else None,
        'include_context_sections': [section.value for section in context_sections(context)],
        'dry_run': payload.dry_run,
        'lab_context': context.model_dump(mode='json'),
        'action_catalog': abrain_actions.get_catalog().model_dump(mode='json'),
    }
    result = abrain_client.query(request_payload)
    if not result.success or result.payload is None:
        if settings.abrain_use_local_fallback:
            return None
        return _empty_response(
            payload=payload,
            context=context,
            mode='external',
            fallback_used=False,
            summary='Externes ABrain nicht erreichbar und lokaler Fallback deaktiviert.',
            policy_decision='external_unavailable',
        )
    return _normalize_external_response(result.payload, payload, context, trace_id=result.trace_id)


def _normalize_external_response(
    raw: dict[str, Any],
    payload: ABrainAdapterQueryRequest,
    context: ABrainAdapterContextRead,
    *,
    trace_id: str | None,
) -> ABrainAdapterResponse:
    recommended: list[ABrainAdapterRecommendedAction] = []
    blocked: list[ABrainAdapterRecommendedAction] = []
    for raw_action in raw.get('recommended_actions', []) or []:
        action = _coerce_action(raw_action)
        if action is None:
            continue
        if action.blocked:
            blocked.append(action)
        else:
            recommended.append(action)
    for raw_action in raw.get('blocked_actions', []) or []:
        action = _coerce_action(raw_action)
        if action is not None:
            action = action.model_copy(update={'blocked': True})
            blocked.append(action)
    approval_required = bool(raw.get('approval_required')) or any(item.requires_approval for item in recommended)
    return ABrainAdapterResponse(
        question=payload.question,
        preset=payload.preset,
        mode='external',
        fallback_used=False,
        contract_version=_CONTRACT_VERSION,
        trace_id=trace_id or str(raw.get('trace_id') or ''),
        summary=str(raw.get('summary') or 'Externes ABrain hat eine Empfehlung erzeugt.'),
        highlights=[str(item) for item in raw.get('highlights', []) or []],
        recommended_actions=recommended,
        blocked_actions=blocked,
        approval_required=approval_required,
        policy_decision=str(raw.get('policy_decision')) if raw.get('policy_decision') is not None else None,
        used_context_sections=payload.include_context_sections or abrain_context.default_sections(),
        referenced_entities=[],
        notes=[str(item) for item in raw.get('notes', []) or []],
    )


def _coerce_action(raw: Any) -> ABrainAdapterRecommendedAction | None:
    if not isinstance(raw, dict):
        return None
    name = str(raw.get('action') or raw.get('name') or '').strip()
    if not name:
        return None
    descriptor = abrain_actions.find_action(name)
    if descriptor is None:
        return ABrainAdapterRecommendedAction(
            action=name,
            target=str(raw.get('target')) if raw.get('target') is not None else None,
            reason=str(raw.get('reason') or 'Unbekannte Action. LabOS erlaubt nur gelistete Aktionen.'),
            risk_level=ABrainActionRiskLevel.medium,
            requires_approval=True,
            blocked=True,
            blocked_reason='action_not_in_catalog',
        )
    requires_approval = bool(raw.get('requires_approval', descriptor.requires_approval))
    blocked = bool(raw.get('blocked', False))
    blocked_reason = raw.get('blocked_reason')
    return ABrainAdapterRecommendedAction(
        action=descriptor.name,
        target=str(raw.get('target')) if raw.get('target') is not None else None,
        reason=str(raw.get('reason') or descriptor.description),
        risk_level=descriptor.risk_level,
        requires_approval=requires_approval or descriptor.requires_approval,
        blocked=blocked,
        blocked_reason=str(blocked_reason) if blocked_reason is not None else None,
    )


def _build_local_response(
    context: ABrainAdapterContextRead,
    payload: ABrainAdapterQueryRequest,
    *,
    fallback_used: bool,
) -> ABrainAdapterResponse:
    highlights = _build_local_highlights(context)
    recommended = _build_local_recommendations(context)
    approval_required = any(item.requires_approval for item in recommended)
    notes: list[str] = []
    if fallback_used:
        notes.append('Externes ABrain nicht erreichbar. Lokale Adapter-Logik verwendet.')
    else:
        notes.append('Lokale Adapter-Logik aktiv (kein externes ABrain konfiguriert).')
    summary = _build_local_summary(context)
    return ABrainAdapterResponse(
        question=payload.question,
        preset=payload.preset,
        mode='local',
        fallback_used=fallback_used,
        contract_version=_CONTRACT_VERSION,
        trace_id=_new_trace_id(),
        summary=summary,
        highlights=highlights,
        recommended_actions=recommended,
        blocked_actions=[],
        approval_required=approval_required,
        policy_decision='local_rules_v1',
        used_context_sections=payload.include_context_sections or abrain_context.default_sections(),
        referenced_entities=[],
        notes=notes,
    )


def _build_local_summary(context: ABrainAdapterContextRead) -> str:
    summary = context.summary
    ops = context.operations
    return (
        f'Offene Aufgaben: {summary.open_tasks} (davon {summary.overdue_tasks} ueberfaellig). '
        f'Kritische Alerts: {summary.critical_alerts}. '
        f'Offene Safety-Incidents: {ops.open_safety_incident_count}. '
        f'Blockierte Commands: {ops.blocked_command_count}, fehlgeschlagen: {ops.failed_command_count}.'
    )


def _build_local_highlights(context: ABrainAdapterContextRead) -> list[str]:
    highlights: list[str] = []
    for reactor in context.reactors:
        if reactor.health_status in {'incident', 'warning'}:
            suffix = f' ({reactor.health_summary})' if reactor.health_summary else ''
            highlights.append(f"Reaktor '{reactor.name}' Health={reactor.health_status}{suffix}.")
    for alert in context.operations.critical_alerts[:3]:
        highlights.append(f"Kritischer Alert '{alert.title}' ({alert.severity}).")
    for task in context.operations.overdue_tasks[:3]:
        highlights.append(f"Ueberfaelliger Task '{task.title}' (prio {task.priority}).")
    if context.operations.blocked_command_count > 0:
        highlights.append(f'{context.operations.blocked_command_count} Reactor-Commands sind aktuell blockiert.')
    if context.operations.failed_command_count > 0:
        highlights.append(f'{context.operations.failed_command_count} Reactor-Commands sind fehlgeschlagen oder abgelaufen.')
    if context.operations.due_calibration_count > 0:
        highlights.append(f'{context.operations.due_calibration_count} Kalibrierungen sind faellig oder abgelaufen.')
    if context.operations.overdue_maintenance_count > 0:
        highlights.append(f'{context.operations.overdue_maintenance_count} Wartungen sind ueberfaellig.')
    if not highlights:
        highlights.append('Aktuell keine kritischen Auffaelligkeiten im Kontext.')
    return highlights[:8]


def _build_local_recommendations(context: ABrainAdapterContextRead) -> list[ABrainAdapterRecommendedAction]:
    actions: list[ABrainAdapterRecommendedAction] = []

    def _push(name: str, *, target: str | None, reason: str) -> None:
        descriptor = abrain_actions.find_action(name)
        if descriptor is None:
            return
        actions.append(_as_recommendation(descriptor, target=target, reason=reason))

    for reactor in context.reactors:
        if reactor.open_incident_count > 0 and reactor.health_status in {'incident', 'warning'}:
            _push(
                'labos.run_reactor_health_assessment',
                target=f'reactor:{reactor.id}',
                reason=f"Reaktor '{reactor.name}' hat offene Incidents und Health={reactor.health_status}.",
            )
    for alert in context.operations.critical_alerts[:2]:
        _push(
            'labos.create_task',
            target=f'alert:{alert.id}',
            reason=f"Kritischer Alert '{alert.title}' sollte als Task nachverfolgt werden.",
        )
    if context.operations.open_safety_incident_count > 0:
        _push(
            'labos.ack_safety_incident',
            target=None,
            reason='Offene Safety-Incidents sollten bewertet und quittiert werden.',
        )
    if context.operations.blocked_command_count > 0:
        _push(
            'labos.retry_reactor_command',
            target=None,
            reason='Blockierte Reactor-Commands pruefen und ggf. erneut einplanen.',
        )
    if context.operations.due_calibration_count > 0:
        _push(
            'labos.create_calibration_record',
            target=None,
            reason='Faellige oder abgelaufene Kalibrierungen nachholen.',
        )
    if context.operations.overdue_maintenance_count > 0:
        _push(
            'labos.create_maintenance_record',
            target=None,
            reason='Ueberfaellige Wartungen einplanen.',
        )
    return actions[:6]


def _as_recommendation(
    descriptor: ABrainActionDescriptor,
    *,
    target: str | None,
    reason: str,
) -> ABrainAdapterRecommendedAction:
    return ABrainAdapterRecommendedAction(
        action=descriptor.name,
        target=target,
        reason=reason,
        risk_level=descriptor.risk_level,
        requires_approval=descriptor.requires_approval,
        blocked=False,
        blocked_reason=None,
    )


def _empty_response(
    *,
    payload: ABrainAdapterQueryRequest,
    context: ABrainAdapterContextRead,
    mode: str,
    fallback_used: bool,
    summary: str,
    policy_decision: str,
) -> ABrainAdapterResponse:
    return ABrainAdapterResponse(
        question=payload.question,
        preset=payload.preset,
        mode=mode,
        fallback_used=fallback_used,
        contract_version=_CONTRACT_VERSION,
        trace_id=_new_trace_id(),
        summary=summary,
        highlights=[],
        recommended_actions=[],
        blocked_actions=[],
        approval_required=False,
        policy_decision=policy_decision,
        used_context_sections=payload.include_context_sections or abrain_context.default_sections(),
        referenced_entities=[],
        notes=[summary],
    )


def _current_mode() -> str:
    if not abrain_client.is_enabled() or settings.abrain_use_stub:
        return 'local'
    return abrain_client.mode()


def context_sections(context: ABrainAdapterContextRead) -> list[ABrainContextSection]:
    _ = context
    return abrain_context.default_sections()


def _new_trace_id() -> str:
    return f'labos-{_utcnow().strftime("%Y%m%dT%H%M%S")}-{uuid.uuid4().hex[:8]}'
