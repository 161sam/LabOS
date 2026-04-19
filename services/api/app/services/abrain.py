from dataclasses import dataclass
from typing import Any

import httpx
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
    if settings.abrain_use_stub:
        return ABrainStatusRead(
            connected=False,
            mode='stub',
            base_url=settings.abrain_base_url,
            timeout_seconds=settings.abrain_timeout_seconds,
            fallback_available=True,
            note='ABrain läuft im lokalen Stub-Modus auf Basis echter LabOS-Kontextdaten.',
        )

    try:
        with httpx.Client(timeout=settings.abrain_timeout_seconds) as client:
            response = client.get(f"{settings.abrain_base_url.rstrip('/')}/healthz")
            response.raise_for_status()
        return ABrainStatusRead(
            connected=True,
            mode='external',
            base_url=settings.abrain_base_url,
            timeout_seconds=settings.abrain_timeout_seconds,
            fallback_available=True,
            note='Externes ABrain ist erreichbar. LabOS kann Anfragen mit strukturiertem Kontext senden.',
        )
    except Exception:
        return ABrainStatusRead(
            connected=False,
            mode='external',
            base_url=settings.abrain_base_url,
            timeout_seconds=settings.abrain_timeout_seconds,
            fallback_available=True,
            note='Externes ABrain ist aktuell nicht erreichbar. LabOS faellt auf die lokale Assistenzlogik zurueck.',
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
    preset_definition = _PRESETS.get(payload.preset) if payload.preset is not None else None
    if payload.preset is not None and preset_definition is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Unknown ABrain preset')

    used_sections = payload.include_context_sections or (
        preset_definition.default_sections if preset_definition is not None else _ALL_SECTIONS
    )
    context = build_lab_context(session, include_sections=used_sections)

    if settings.abrain_use_stub:
        return _build_local_response(context, payload, fallback_used=False, note='Lokale Assistenzlogik verwendet.')

    try:
        external_payload = _call_external_abrain(context, payload)
        return _normalize_external_response(external_payload, payload, used_sections)
    except Exception:
        return _build_local_response(
            context,
            payload,
            fallback_used=True,
            note='Externes ABrain nicht erreichbar. Lokale Assistenzlogik verwendet.',
        )


def _call_external_abrain(context: ABrainContextRead, payload: ABrainQueryRequest) -> dict[str, Any]:
    request_payload = {
        'question': payload.question,
        'preset': payload.preset.value if payload.preset is not None else None,
        'lab_context': context.model_dump(mode='json'),
        'include_context_sections': [section.value for section in context.included_sections],
    }
    with httpx.Client(timeout=settings.abrain_timeout_seconds) as client:
        response = client.post(f"{settings.abrain_base_url.rstrip('/')}/query", json=request_payload)
        response.raise_for_status()
        return response.json()


def _normalize_external_response(
    payload: dict[str, Any],
    request: ABrainQueryRequest,
    used_sections: list[ABrainContextSection],
) -> ABrainQueryResponse:
    referenced_entities = [
        ABrainReferenceRead(
            entity_type=str(item.get('entity_type', 'unknown')),
            entity_id=int(item.get('entity_id', 0)),
            label=str(item.get('label', '')),
        )
        for item in payload.get('referenced_entities', [])
        if item.get('entity_id') is not None
    ]
    return ABrainQueryResponse(
        question=request.question,
        preset=request.preset,
        mode='external',
        fallback_used=False,
        summary=str(payload.get('summary', 'ABrain hat eine Antwort auf Basis des LabOS-Kontexts erzeugt.')),
        highlights=[str(item) for item in payload.get('highlights', [])],
        recommended_actions=[str(item) for item in payload.get('recommended_actions', [])],
        referenced_entities=referenced_entities,
        used_context_sections=used_sections,
        note=str(payload.get('note')) if payload.get('note') is not None else None,
    )


def _build_local_response(
    context: ABrainContextRead,
    payload: ABrainQueryRequest,
    fallback_used: bool,
    note: str | None,
) -> ABrainQueryResponse:
    highlights: list[str] = []
    recommended_actions: list[str] = []
    references: list[ABrainReferenceRead] = []

    if payload.preset == ABrainPreset.overdue_tasks:
        _append_task_highlights(context, highlights, recommended_actions, references, only_overdue=True)
    elif payload.preset == ABrainPreset.sensor_attention:
        _append_sensor_highlights(context, highlights, recommended_actions, references)
    elif payload.preset == ABrainPreset.reactor_attention:
        _append_reactor_highlights(context, highlights, recommended_actions, references)
    elif payload.preset == ABrainPreset.recent_activity:
        _append_recent_activity(context, highlights, recommended_actions, references)
    elif payload.preset == ABrainPreset.critical_issues:
        _append_alert_highlights(context, highlights, recommended_actions, references, critical_only=True)
        _append_sensor_highlights(context, highlights, recommended_actions, references)
        _append_task_highlights(context, highlights, recommended_actions, references, only_overdue=True)
    else:
        _append_alert_highlights(context, highlights, recommended_actions, references, critical_only=True)
        _append_task_highlights(context, highlights, recommended_actions, references, only_overdue=False)
        _append_sensor_highlights(context, highlights, recommended_actions, references)
        _append_recent_activity(context, highlights, recommended_actions, references)

    if not highlights:
        highlights.append('Aktuell zeigen die ausgewaehlten Kontextbereiche keine akuten operativen Auffaelligkeiten.')
    if not recommended_actions:
        recommended_actions.append('Regelmaessig Dashboard, Alerts und offene Aufgaben weiter beobachten.')

    summary = _build_summary_text(context, payload.preset)
    return ABrainQueryResponse(
        question=payload.question,
        preset=payload.preset,
        mode='stub',
        fallback_used=fallback_used,
        summary=summary,
        highlights=highlights[:6],
        recommended_actions=recommended_actions[:6],
        referenced_entities=references[:8],
        used_context_sections=context.included_sections,
        note=note,
    )


def _build_summary_text(context: ABrainContextRead, preset: ABrainPreset | None) -> str:
    summary = context.summary
    if preset == ABrainPreset.overdue_tasks:
        return (
            f"Es gibt {summary.overdue_tasks} ueberfaellige Aufgaben und {summary.open_tasks} offene Aufgaben insgesamt."
        )
    if preset == ABrainPreset.sensor_attention:
        return (
            f"Es gibt {summary.sensor_attention} Sensoren mit Aufmerksamkeitsbedarf und {summary.critical_alerts} kritische Alerts."
        )
    if preset == ABrainPreset.reactor_attention:
        reactors_with_tasks = len([reactor for reactor in context.reactors or [] if reactor.open_task_count > 0])
        return (
            f"{reactors_with_tasks} Reaktoren haben offene Aufgaben, bei {summary.reactors_online} Reaktoren ist der Status aktuell online."
        )
    if preset == ABrainPreset.recent_activity:
        return (
            f"Zuletzt wurden {summary.recent_photos} Fotos erfasst; parallel bestehen {summary.open_alerts} offene Alerts."
        )
    if preset == ABrainPreset.critical_issues:
        return (
            f"Aktuell bestehen {summary.critical_alerts} kritische Alerts, {summary.overdue_tasks} ueberfaellige Aufgaben und {summary.sensor_attention} auffaellige Sensorlagen."
        )
    return (
        f"Heute bestehen {summary.open_tasks} offene Aufgaben, {summary.critical_alerts} kritische Alerts, "
        f"{summary.sensor_attention} auffaellige Sensorlagen und {summary.recent_photos} aktuelle Fotoeintraege."
    )


def _append_task_highlights(
    context: ABrainContextRead,
    highlights: list[str],
    actions: list[str],
    references: list[ABrainReferenceRead],
    *,
    only_overdue: bool,
) -> None:
    tasks = context.tasks or []
    filtered_tasks = [
        task for task in tasks if (task.due_at is not None and task.due_at < context.generated_at) or not only_overdue
    ]
    for task in filtered_tasks[:2]:
        due_text = task.due_at.strftime('%d.%m.%Y %H:%M') if task.due_at else 'ohne Termin'
        location = task.charge_name or task.reactor_name or 'ohne Zuordnung'
        highlights.append(
            f"Task '{task.title}' ist {task.status} mit Prioritaet {task.priority} ({location}, faellig {due_text})."
        )
        actions.append(f"Task '{task.title}' priorisieren und Status im Modul Aufgaben aktualisieren.")
        references.append(ABrainReferenceRead(entity_type='task', entity_id=task.id, label=task.title))


def _append_alert_highlights(
    context: ABrainContextRead,
    highlights: list[str],
    actions: list[str],
    references: list[ABrainReferenceRead],
    *,
    critical_only: bool,
) -> None:
    alerts = context.alerts or []
    filtered_alerts = [
        alert for alert in alerts if alert.severity in {'high', 'critical'} or not critical_only
    ]
    for alert in filtered_alerts[:2]:
        highlights.append(
            f"Alert '{alert.title}' ist {alert.status} mit Severity {alert.severity} aus Quelle {alert.source_type}."
        )
        actions.append(f"Alert '{alert.title}' pruefen und bei Bedarf quittieren oder aufloesen.")
        references.append(ABrainReferenceRead(entity_type='alert', entity_id=alert.id, label=alert.title))


def _append_sensor_highlights(
    context: ABrainContextRead,
    highlights: list[str],
    actions: list[str],
    references: list[ABrainReferenceRead],
) -> None:
    for sensor in (context.sensors or [])[:2]:
        reactor_label = sensor.reactor_name or 'ohne Reaktor'
        highlights.append(
            f"Sensor '{sensor.name}' ({reactor_label}) braucht Aufmerksamkeit: {sensor.attention_reason}."
        )
        actions.append(f"Sensor '{sensor.name}' pruefen und aktuellen Messwert oder Status nachziehen.")
        references.append(ABrainReferenceRead(entity_type='sensor', entity_id=sensor.id, label=sensor.name))


def _append_reactor_highlights(
    context: ABrainContextRead,
    highlights: list[str],
    actions: list[str],
    references: list[ABrainReferenceRead],
) -> None:
    reactors = sorted(
        context.reactors or [],
        key=lambda reactor: (0 if reactor.status != 'online' else 1, -reactor.open_task_count, reactor.name),
    )
    for reactor in reactors[:2]:
        if reactor.status != 'online' or reactor.open_task_count > 0:
            highlights.append(
                f"Reaktor '{reactor.name}' steht auf Status {reactor.status} und hat {reactor.open_task_count} offene Tasks."
            )
            actions.append(f"Reaktor '{reactor.name}' inklusive offener Aufgaben und aktuellem Zustand pruefen.")
            references.append(ABrainReferenceRead(entity_type='reactor', entity_id=reactor.id, label=reactor.name))


def _append_recent_activity(
    context: ABrainContextRead,
    highlights: list[str],
    actions: list[str],
    references: list[ABrainReferenceRead],
) -> None:
    if context.photos:
        photo = context.photos[0]
        label = photo.title or f'Foto #{photo.id}'
        vision_note = (
            f" Vision-Einschaetzung: {photo.vision_health_label}"
            if photo.vision_health_label
            else ''
        )
        highlights.append(
            f"Zuletzt wurde '{label}' als Foto-Dokumentation erfasst "
            f"({photo.charge_name or photo.reactor_name or 'ohne Zuordnung'}).{vision_note}"
        )
        actions.append('Aktuelle Bilddokumentation fuer Verlauf und Nachweis in der Fotoansicht pruefen.')
        references.append(ABrainReferenceRead(entity_type='photo', entity_id=photo.id, label=label))


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
