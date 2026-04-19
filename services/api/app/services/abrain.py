"""ABrain legacy surface — THIN ADAPTER FACADE.

This module keeps the legacy `/api/v1/abrain/status|context|presets|query`
endpoints alive while routing their work through the canonical ABrain
adapter layer (`abrain_adapter.py` / `abrain_client.py` / `abrain_context.py`).

THIS IS NOT THE REAL BRAIN. Status and query paths delegate to the
adapter. Presets and legacy `/context` still build their LabOS-specific
shape here, because the frontend legacy UI expects it. No new reasoning
logic lives in this module — all decisions are made in the adapter (or
in the external ABrain behind it), and highlights / actions are
projected back into the legacy `ABrainQueryResponse` shape.
"""
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..config import settings
from ..models import Charge, Reactor, Task, _utcnow
from ..schemas import (
    ABrainAlertContextItemRead,
    ABrainContextRead,
    ABrainContextSection,
    ABrainPhotoContextItemRead,
    ABrainPreset,
    ABrainPresetRead,
    ABrainQueryRequest,
    ABrainQueryResponse,
    ABrainReactorContextItemRead,
    ABrainReferenceRead,
    ABrainSensorAttentionItemRead,
    ABrainStatusRead,
    ABrainSummaryCountsRead,
    ABrainTaskContextItemRead,
    ABrainChargeContextItemRead,
    AlertStatus,
    TaskStatus,
)
from . import abrain_adapter
from . import alerts as alert_service
from . import photos as photo_service
from . import reactor_health as reactor_health_service
from . import sensors as sensor_service
from . import tasks as task_service
from . import vision as vision_service

_ALL_SECTIONS = [
    ABrainContextSection.tasks,
    ABrainContextSection.alerts,
    ABrainContextSection.sensors,
    ABrainContextSection.charges,
    ABrainContextSection.reactors,
    ABrainContextSection.photos,
]
_STALE_SENSOR_HOURS = 6


@dataclass(frozen=True)
class _PresetDefinition:
    id: ABrainPreset
    title: str
    description: str
    default_question: str
    default_sections: list[ABrainContextSection]


_PRESETS = {
    ABrainPreset.daily_overview: _PresetDefinition(
        id=ABrainPreset.daily_overview,
        title='Tagesueberblick',
        description='Fasst die wichtigsten offenen Punkte fuer den aktuellen Labortag zusammen.',
        default_question='Was sind die wichtigsten offenen Punkte im Labor heute?',
        default_sections=_ALL_SECTIONS,
    ),
    ABrainPreset.critical_issues: _PresetDefinition(
        id=ABrainPreset.critical_issues,
        title='Kritische Themen',
        description='Fokussiert auf kritische Alerts, Sensorprobleme und blockierte Arbeit.',
        default_question='Welche kritischen Themen brauchen jetzt Aufmerksamkeit?',
        default_sections=[
            ABrainContextSection.alerts,
            ABrainContextSection.sensors,
            ABrainContextSection.tasks,
            ABrainContextSection.reactors,
        ],
    ),
    ABrainPreset.overdue_tasks: _PresetDefinition(
        id=ABrainPreset.overdue_tasks,
        title='Ueberfaellige Aufgaben',
        description='Zeigt ueberfaellige oder eskalierende operative Aufgaben.',
        default_question='Welche Aufgaben sind ueberfaellig oder besonders dringlich?',
        default_sections=[ABrainContextSection.tasks, ABrainContextSection.alerts],
    ),
    ABrainPreset.sensor_attention: _PresetDefinition(
        id=ABrainPreset.sensor_attention,
        title='Sensor Aufmerksamkeit',
        description='Fokussiert auf fehlerhafte oder veraltete Sensorlagen.',
        default_question='Welche Sensoren brauchen aktuell Aufmerksamkeit?',
        default_sections=[ABrainContextSection.sensors, ABrainContextSection.alerts],
    ),
    ABrainPreset.reactor_attention: _PresetDefinition(
        id=ABrainPreset.reactor_attention,
        title='Reaktor Aufmerksamkeit',
        description='Zeigt Reaktoren mit offenen Aufgaben oder problematischen Zustaenden.',
        default_question='Welche Reaktoren brauchen aktuell Aufmerksamkeit?',
        default_sections=[ABrainContextSection.reactors, ABrainContextSection.tasks, ABrainContextSection.alerts],
    ),
    ABrainPreset.recent_activity: _PresetDefinition(
        id=ABrainPreset.recent_activity,
        title='Letzte Aktivitaet',
        description='Fokussiert auf frische Uploads, Alerts und laufende Arbeit.',
        default_question='Was ist die juengste relevante Aktivitaet im Labor?',
        default_sections=[ABrainContextSection.photos, ABrainContextSection.alerts, ABrainContextSection.tasks],
    ),
}


def get_status() -> ABrainStatusRead:
    """Legacy status facade — delegates to the adapter.

    Translates the adapter's `local` mode back to the legacy `stub`
    label whenever `ABRAIN_USE_STUB` is active, so existing UI clients
    keep seeing the expected value.
    """
    adapter_status = abrain_adapter.get_status()
    effective_mode = adapter_status.mode
    if settings.abrain_use_stub and effective_mode == 'local':
        effective_mode = 'stub'
    note = adapter_status.note
    if effective_mode == 'stub':
        note = 'ABrain läuft im lokalen Stub-Modus auf Basis echter LabOS-Kontextdaten.'
    return ABrainStatusRead(
        connected=adapter_status.connected,
        mode=effective_mode,
        base_url=adapter_status.base_url,
        timeout_seconds=adapter_status.timeout_seconds,
        fallback_available=adapter_status.fallback_available,
        note=note,
    )


def list_presets() -> list[ABrainPresetRead]:
    return [
        ABrainPresetRead(
            id=definition.id,
            title=definition.title,
            description=definition.description,
            default_question=definition.default_question,
            default_sections=definition.default_sections,
        )
        for definition in _PRESETS.values()
    ]


def build_lab_context(
    session: Session,
    include_sections: list[ABrainContextSection] | None = None,
) -> ABrainContextRead:
    included_sections = include_sections or _ALL_SECTIONS
    now = _utcnow()

    task_items = task_service.list_tasks(session)
    alert_items = alert_service.list_alerts(session)
    sensor_items = sensor_service.list_sensors(session)
    recent_photos = photo_service.list_photos(session, latest=True, limit=5)
    active_charges = list(session.exec(select(Charge).where(Charge.status == 'active')).all())
    reactors = list(session.exec(select(Reactor).order_by(Reactor.name.asc(), Reactor.id.asc())).all())

    open_tasks = [task for task in task_items if task.status != TaskStatus.done]
    overdue_tasks = [task for task in open_tasks if task.due_at is not None and task.due_at < now]
    due_today_tasks = [
        task
        for task in open_tasks
        if task.due_at is not None and task.due_at.date() == now.date()
    ]
    critical_alerts = [
        alert
        for alert in alert_items
        if alert.status != AlertStatus.resolved and alert.severity in {'high', 'critical'}
    ]
    open_alerts = [alert for alert in alert_items if alert.status != AlertStatus.resolved]
    sensor_attention = _collect_sensor_attention(sensor_items, now)
    reactor_open_task_count = {
        reactor.id: sum(1 for task in open_tasks if task.reactor_id == reactor.id)
        for reactor in reactors
    }

    return ABrainContextRead(
        generated_at=now,
        included_sections=included_sections,
        summary=ABrainSummaryCountsRead(
            open_tasks=len(open_tasks),
            overdue_tasks=len(overdue_tasks),
            due_today_tasks=len(due_today_tasks),
            critical_alerts=len(critical_alerts),
            open_alerts=len(open_alerts),
            sensor_attention=len(sensor_attention),
            active_charges=len(active_charges),
            reactors_online=sum(1 for reactor in reactors if reactor.status == 'online'),
            recent_photos=len(recent_photos),
        ),
        tasks=_build_task_section(included_sections, open_tasks, overdue_tasks, due_today_tasks),
        alerts=_build_alert_section(included_sections, critical_alerts, open_alerts),
        sensors=_build_sensor_section(included_sections, sensor_attention),
        charges=_build_charge_section(included_sections, active_charges),
        reactors=_build_reactor_section(
            included_sections,
            reactors,
            reactor_open_task_count,
            reactor_health_service.get_latest_for_reactors(session, [reactor.id for reactor in reactors]),
        ),
        photos=_build_photo_section(included_sections, recent_photos),
    )


def query(session: Session, payload: ABrainQueryRequest) -> ABrainQueryResponse:
    """Legacy query facade — delegates to the adapter orchestrator.

    Resolves the requested preset, asks the adapter to build context +
    talk to external ABrain (or local fallback), then projects the
    richer `ABrainAdapterResponse` into the legacy `ABrainQueryResponse`
    shape that the existing frontend expects.
    """
    preset_definition = _PRESETS.get(payload.preset) if payload.preset is not None else None
    if payload.preset is not None and preset_definition is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Unknown ABrain preset')

    used_sections = payload.include_context_sections or (
        preset_definition.default_sections if preset_definition is not None else _ALL_SECTIONS
    )

    from ..schemas import ABrainAdapterQueryRequest
    adapter_payload = ABrainAdapterQueryRequest(
        question=payload.question,
        preset=payload.preset,
        include_context_sections=used_sections,
        dry_run=True,
    )
    adapter_response = abrain_adapter.query_adapter(session, adapter_payload)

    effective_mode = 'stub' if adapter_response.mode == 'local' else adapter_response.mode

    recommended_texts = _project_actions_to_text(adapter_response.recommended_actions)
    if not recommended_texts:
        recommended_texts = ['Regelmaessig Dashboard, Alerts und offene Aufgaben weiter beobachten.']

    highlights = list(adapter_response.highlights)
    if not highlights:
        highlights = ['Aktuell zeigen die ausgewaehlten Kontextbereiche keine akuten operativen Auffaelligkeiten.']

    if effective_mode == 'stub':
        note = (
            'Externes ABrain nicht erreichbar. Lokale Assistenzlogik verwendet.'
            if adapter_response.fallback_used
            else 'Lokale Assistenzlogik verwendet.'
        )
    else:
        note = adapter_response.notes[0] if adapter_response.notes else None

    return ABrainQueryResponse(
        question=payload.question,
        preset=payload.preset,
        mode=effective_mode,
        fallback_used=adapter_response.fallback_used,
        summary=adapter_response.summary,
        highlights=highlights[:6],
        recommended_actions=recommended_texts[:6],
        referenced_entities=list(adapter_response.referenced_entities),
        used_context_sections=used_sections,
        note=note,
    )


def _project_actions_to_text(
    actions: list[Any],
) -> list[str]:
    texts: list[str] = []
    for item in actions:
        if item.blocked:
            continue
        approval_hint = ' (Freigabe erforderlich)' if item.requires_approval else ''
        target_hint = f' → {item.target}' if item.target else ''
        texts.append(f'{item.action}{target_hint}: {item.reason}{approval_hint}')
    return texts


def _build_task_section(
    included_sections: list[ABrainContextSection],
    open_tasks: list[Any],
    overdue_tasks: list[Any],
    due_today_tasks: list[Any],
) -> list[ABrainTaskContextItemRead] | None:
    if ABrainContextSection.tasks not in included_sections:
        return None
    selected = overdue_tasks[:3]
    if len(selected) < 3:
        selected.extend(task for task in due_today_tasks if task not in selected)
    if len(selected) < 3:
        selected.extend(task for task in open_tasks if task not in selected)
    return [
        ABrainTaskContextItemRead(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            charge_name=task.charge_name,
            reactor_name=task.reactor_name,
        )
        for task in selected[:5]
    ]


def _build_alert_section(
    included_sections: list[ABrainContextSection],
    critical_alerts: list[Any],
    open_alerts: list[Any],
) -> list[ABrainAlertContextItemRead] | None:
    if ABrainContextSection.alerts not in included_sections:
        return None
    selected = critical_alerts[:3]
    if len(selected) < 3:
        selected.extend(alert for alert in open_alerts if alert not in selected)
    return [
        ABrainAlertContextItemRead(
            id=alert.id,
            title=alert.title,
            severity=alert.severity,
            status=alert.status,
            source_type=alert.source_type,
            created_at=alert.created_at,
        )
        for alert in selected[:5]
    ]


def _build_sensor_section(
    included_sections: list[ABrainContextSection],
    sensor_attention: list[ABrainSensorAttentionItemRead],
) -> list[ABrainSensorAttentionItemRead] | None:
    if ABrainContextSection.sensors not in included_sections:
        return None
    return sensor_attention[:5]


def _build_charge_section(
    included_sections: list[ABrainContextSection],
    active_charges: list[Charge],
) -> list[ABrainChargeContextItemRead] | None:
    if ABrainContextSection.charges not in included_sections:
        return None
    return [
        ABrainChargeContextItemRead(
            id=charge.id,
            name=charge.name,
            species=charge.species,
            status=charge.status,
        )
        for charge in active_charges[:5]
    ]


_HEALTH_PRIORITY = {
    'incident': 0,
    'warning': 1,
    'attention': 2,
    'unknown': 3,
    'nominal': 4,
}


def _build_reactor_section(
    included_sections: list[ABrainContextSection],
    reactors: list[Reactor],
    reactor_open_task_count: dict[int, int],
    health_map: dict[int, Any] | None = None,
) -> list[ABrainReactorContextItemRead] | None:
    if ABrainContextSection.reactors not in included_sections:
        return None
    health_map = health_map or {}
    sorted_reactors = sorted(
        reactors,
        key=lambda reactor: (
            _HEALTH_PRIORITY.get(health_map[reactor.id].status, 4) if reactor.id in health_map else 3,
            0 if reactor.status != 'online' else 1,
            -reactor_open_task_count.get(reactor.id, 0),
            reactor.name,
        ),
    )
    return [
        ABrainReactorContextItemRead(
            id=reactor.id,
            name=reactor.name,
            status=reactor.status,
            open_task_count=reactor_open_task_count.get(reactor.id, 0),
            health_status=health_map[reactor.id].status if reactor.id in health_map else None,
            health_summary=health_map[reactor.id].summary if reactor.id in health_map else None,
            health_assessed_at=health_map[reactor.id].assessed_at if reactor.id in health_map else None,
        )
        for reactor in sorted_reactors[:5]
    ]


def _build_photo_section(
    included_sections: list[ABrainContextSection],
    recent_photos: list[Any],
) -> list[ABrainPhotoContextItemRead] | None:
    if ABrainContextSection.photos not in included_sections:
        return None
    items: list[ABrainPhotoContextItemRead] = []
    for photo in recent_photos[:5]:
        vision = photo.latest_vision if getattr(photo, 'latest_vision', None) is not None else None
        vision_result = vision.result if vision is not None else {}
        items.append(
            ABrainPhotoContextItemRead(
                id=photo.id,
                title=photo.title,
                created_at=photo.created_at,
                captured_at=photo.captured_at,
                charge_name=photo.charge_name,
                reactor_name=photo.reactor_name,
                vision_health_label=vision_result.get('health_label') if vision_result else None,
                vision_green_ratio=vision_result.get('green_ratio') if vision_result else None,
                vision_brown_ratio=vision_result.get('brown_ratio') if vision_result else None,
                vision_confidence=vision.confidence if vision is not None else None,
            )
        )
    return items


def _collect_sensor_attention(sensor_items: list[Any], now) -> list[ABrainSensorAttentionItemRead]:
    attention_items: list[ABrainSensorAttentionItemRead] = []
    for sensor in sensor_items:
        reason = None
        if sensor.status == 'error':
            reason = 'Status steht auf Fehler'
        elif sensor.last_recorded_at is None:
            reason = 'Noch kein aktueller Messwert vorhanden'
        elif (now - sensor.last_recorded_at).total_seconds() > _STALE_SENSOR_HOURS * 3600:
            reason = f'Letzter Messwert ist aelter als {_STALE_SENSOR_HOURS} Stunden'

        if reason is not None:
            attention_items.append(
                ABrainSensorAttentionItemRead(
                    id=sensor.id,
                    name=sensor.name,
                    status=sensor.status,
                    reactor_name=sensor.reactor_name,
                    last_recorded_at=sensor.last_recorded_at,
                    last_value=sensor.last_value,
                    attention_reason=reason,
                )
            )
    return attention_items
