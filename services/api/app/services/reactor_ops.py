from __future__ import annotations

from collections import Counter
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Alert, Charge, Photo, Reactor, ReactorEvent, ReactorTwin, Sensor, Task, UserAccount, _utcnow
from ..schemas import (
    AlertRead,
    AlertStatus,
    ChargeRead,
    PhotoRead,
    ReactorBiologicalState,
    ReactorContaminationState,
    ReactorEventCreate,
    ReactorEventRead,
    ReactorPhase,
    ReactorTechnicalState,
    ReactorTwinCreate,
    ReactorTwinDetailRead,
    ReactorTwinPhaseUpdate,
    ReactorTwinRead,
    ReactorTwinStateUpdate,
    ReactorTwinUpdate,
)
from . import photos as photo_service
from . import sensors as sensor_service
from . import tasks as task_service

_CURRENT_CHARGE_STATUSES = {'planned', 'active', 'paused'}
_OPEN_TASK_STATUSES = {'open', 'doing', 'blocked'}
_INCIDENT_PHASES = {ReactorPhase.incident.value}
_ATTENTION_TECHNICAL_STATES = {
    ReactorTechnicalState.warning.value,
    ReactorTechnicalState.degraded.value,
    ReactorTechnicalState.error.value,
}
_INCIDENT_CONTAMINATION_STATES = {
    ReactorContaminationState.suspected.value,
    ReactorContaminationState.confirmed.value,
}


def list_reactor_ops(session: Session) -> list[ReactorTwinRead]:
    reactors = list(session.exec(select(Reactor).order_by(Reactor.name.asc(), Reactor.id.asc())).all())
    return _serialize_reactor_twin_reads(session, reactors)


def get_reactor_ops(session: Session, reactor_id: int) -> ReactorTwinDetailRead:
    reactor = get_reactor_or_404(session, reactor_id)
    summary = _serialize_reactor_twin_reads(session, [reactor])[0]
    open_tasks = task_service.list_tasks(session, reactor_id=reactor_id)
    open_tasks = [task for task in open_tasks if task.status in _OPEN_TASK_STATUSES][:6]
    recent_alerts = list_reactor_alerts(session, reactor_id=reactor_id, limit=6)
    recent_photos = photo_service.list_photos(session, reactor_id=reactor_id, latest=True, limit=6)
    recent_events = list_reactor_events(session, reactor_id=reactor_id, limit=8)
    recent_sensors = sensor_service.list_reactor_sensors(session, reactor_id=reactor_id, limit=6)
    return ReactorTwinDetailRead(
        **summary.model_dump(),
        recent_events=recent_events,
        open_tasks=open_tasks,
        recent_alerts=recent_alerts,
        recent_photos=recent_photos,
        recent_sensors=recent_sensors,
    )


def create_reactor_twin(session: Session, payload: ReactorTwinCreate) -> ReactorTwinRead:
    reactor = get_reactor_or_404(session, payload.reactor_id)
    existing = _get_twin(session, payload.reactor_id)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Reactor twin already exists')

    twin = ReactorTwin(reactor_id=reactor.id)
    _apply_twin_payload(twin, payload)
    session.add(twin)
    session.commit()
    return _serialize_reactor_twin_reads(session, [reactor])[0]


def upsert_reactor_twin(session: Session, reactor_id: int, payload: ReactorTwinUpdate) -> ReactorTwinRead:
    reactor = get_reactor_or_404(session, reactor_id)
    twin = _get_twin(session, reactor_id)
    if twin is None:
        twin = ReactorTwin(reactor_id=reactor.id)
    _apply_twin_payload(twin, payload)
    twin.updated_at = _utcnow()
    session.add(twin)
    session.commit()
    return _serialize_reactor_twin_reads(session, [reactor])[0]


def update_reactor_twin_phase(session: Session, reactor_id: int, payload: ReactorTwinPhaseUpdate) -> ReactorTwinRead:
    reactor = get_reactor_or_404(session, reactor_id)
    twin = _get_or_create_twin(session, reactor_id)
    twin.current_phase = payload.current_phase.value
    twin.updated_at = _utcnow()
    session.add(twin)
    session.commit()
    return _serialize_reactor_twin_reads(session, [reactor])[0]


def update_reactor_twin_state(session: Session, reactor_id: int, payload: ReactorTwinStateUpdate) -> ReactorTwinRead:
    reactor = get_reactor_or_404(session, reactor_id)
    twin = _get_or_create_twin(session, reactor_id)
    twin.technical_state = payload.technical_state.value
    twin.biological_state = payload.biological_state.value
    twin.contamination_state = payload.contamination_state.value if payload.contamination_state else None
    twin.updated_at = _utcnow()
    session.add(twin)
    session.commit()
    return _serialize_reactor_twin_reads(session, [reactor])[0]


def list_reactor_events(session: Session, reactor_id: int, limit: int = 20) -> list[ReactorEventRead]:
    get_reactor_or_404(session, reactor_id)
    statement = (
        select(ReactorEvent)
        .where(ReactorEvent.reactor_id == reactor_id)
        .order_by(ReactorEvent.created_at.desc(), ReactorEvent.id.desc())
        .limit(limit)
    )
    events = list(session.exec(statement).all())
    return _serialize_events(session, events)


def create_reactor_event(
    session: Session,
    reactor_id: int,
    payload: ReactorEventCreate,
    *,
    created_by_user_id: int | None = None,
) -> ReactorEventRead:
    get_reactor_or_404(session, reactor_id)
    twin = _get_twin(session, reactor_id)
    event = ReactorEvent(
        reactor_id=reactor_id,
        event_type=payload.event_type.value,
        title=payload.title,
        description=payload.description,
        severity=payload.severity.value if payload.severity else None,
        phase_snapshot=payload.phase_snapshot.value if payload.phase_snapshot else twin.current_phase if twin else None,
        created_by_user_id=created_by_user_id,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return _serialize_events(session, [event])[0]


def create_default_twin_for_reactor(session: Session, reactor_id: int) -> ReactorTwin:
    existing = _get_twin(session, reactor_id)
    if existing is not None:
        return existing

    twin = ReactorTwin(reactor_id=reactor_id)
    session.add(twin)
    session.commit()
    session.refresh(twin)
    return twin


def count_reactors_with_attention(session: Session) -> int:
    twins = list(session.exec(select(ReactorTwin)).all())
    return sum(1 for twin in twins if twin.technical_state in _ATTENTION_TECHNICAL_STATES)


def count_harvest_ready_reactors(session: Session) -> int:
    return len(
        session.exec(select(ReactorTwin.id).where(ReactorTwin.current_phase == ReactorPhase.harvest_ready.value)).all()
    )


def count_reactors_with_incident_or_contamination(session: Session) -> int:
    twins = list(session.exec(select(ReactorTwin)).all())
    return sum(
        1
        for twin in twins
        if twin.current_phase in _INCIDENT_PHASES or twin.contamination_state in _INCIDENT_CONTAMINATION_STATES
    )


def list_recent_events(session: Session, limit: int = 6) -> list[ReactorEventRead]:
    events = list(
        session.exec(
            select(ReactorEvent).order_by(ReactorEvent.created_at.desc(), ReactorEvent.id.desc()).limit(limit)
        ).all()
    )
    return _serialize_events(session, events)


def list_reactor_alerts(session: Session, reactor_id: int, limit: int = 6) -> list[AlertRead]:
    statement = (
        select(Alert)
        .where(Alert.source_type == 'reactor', Alert.source_id == reactor_id)
        .order_by(Alert.created_at.desc(), Alert.id.desc())
        .limit(limit)
    )
    alerts = list(session.exec(statement).all())
    return [AlertRead.model_validate(alert) for alert in alerts]


def get_reactor_or_404(session: Session, reactor_id: int) -> Reactor:
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    return reactor


def _get_twin(session: Session, reactor_id: int) -> ReactorTwin | None:
    return session.exec(select(ReactorTwin).where(ReactorTwin.reactor_id == reactor_id)).first()


def _get_or_create_twin(session: Session, reactor_id: int) -> ReactorTwin:
    twin = _get_twin(session, reactor_id)
    if twin is not None:
        return twin
    return ReactorTwin(reactor_id=reactor_id)


def _apply_twin_payload(twin: ReactorTwin, payload: ReactorTwinCreate | ReactorTwinUpdate) -> None:
    twin.culture_type = payload.culture_type
    twin.strain = payload.strain
    twin.medium_recipe = payload.medium_recipe
    twin.inoculated_at = payload.inoculated_at
    twin.current_phase = payload.current_phase.value
    twin.target_ph_min = payload.target_ph_min
    twin.target_ph_max = payload.target_ph_max
    twin.target_temp_min = payload.target_temp_min
    twin.target_temp_max = payload.target_temp_max
    twin.target_light_min = payload.target_light_min
    twin.target_light_max = payload.target_light_max
    twin.target_flow_min = payload.target_flow_min
    twin.target_flow_max = payload.target_flow_max
    twin.expected_harvest_window_start = payload.expected_harvest_window_start
    twin.expected_harvest_window_end = payload.expected_harvest_window_end
    twin.contamination_state = payload.contamination_state.value if payload.contamination_state else None
    twin.technical_state = payload.technical_state.value
    twin.biological_state = payload.biological_state.value
    twin.notes = payload.notes


def _serialize_reactor_twin_reads(session: Session, reactors: list[Reactor]) -> list[ReactorTwinRead]:
    if not reactors:
        return []

    reactor_ids = [reactor.id for reactor in reactors if reactor.id is not None]
    twins = list(session.exec(select(ReactorTwin).where(ReactorTwin.reactor_id.in_(reactor_ids))).all()) if reactor_ids else []
    charges = (
        list(
            session.exec(
                select(Charge).where(Charge.reactor_id.in_(reactor_ids), Charge.status.in_(_CURRENT_CHARGE_STATUSES))
            ).all()
        )
        if reactor_ids
        else []
    )
    sensors = list(session.exec(select(Sensor.reactor_id).where(Sensor.reactor_id.in_(reactor_ids))).all()) if reactor_ids else []
    tasks = (
        list(
            session.exec(
                select(Task.reactor_id).where(Task.reactor_id.in_(reactor_ids), Task.status.in_(_OPEN_TASK_STATUSES))
            ).all()
        )
        if reactor_ids
        else []
    )
    alerts = (
        list(
            session.exec(
                select(Alert.source_id).where(
                    Alert.source_type == 'reactor',
                    Alert.source_id.in_(reactor_ids),
                    Alert.status != AlertStatus.resolved.value,
                )
            ).all()
        )
        if reactor_ids
        else []
    )
    photos = list(session.exec(select(Photo.reactor_id).where(Photo.reactor_id.in_(reactor_ids))).all()) if reactor_ids else []
    events = (
        list(
            session.exec(
                select(ReactorEvent)
                .where(ReactorEvent.reactor_id.in_(reactor_ids))
                .order_by(ReactorEvent.created_at.desc(), ReactorEvent.id.desc())
            ).all()
        )
        if reactor_ids
        else []
    )

    twin_map = {twin.reactor_id: twin for twin in twins}
    sensor_count_map = Counter(reactor_id for reactor_id in sensors if reactor_id is not None)
    open_task_count_map = Counter(reactor_id for reactor_id in tasks if reactor_id is not None)
    open_alert_count_map = Counter(reactor_id for reactor_id in alerts if reactor_id is not None)
    photo_count_map = Counter(reactor_id for reactor_id in photos if reactor_id is not None)
    current_charge_map = _build_current_charge_map(charges)
    latest_event_map = _build_latest_event_map(session, events)
    latest_vision_map = _build_latest_vision_map(session, reactor_ids)
    latest_health_map = _build_latest_health_map(session, reactor_ids)

    return [
        _to_reactor_twin_read(
            reactor=reactor,
            twin=twin_map.get(reactor.id),
            current_charge=current_charge_map.get(reactor.id),
            sensor_count=sensor_count_map.get(reactor.id, 0),
            open_task_count=open_task_count_map.get(reactor.id, 0),
            open_alert_count=open_alert_count_map.get(reactor.id, 0),
            photo_count=photo_count_map.get(reactor.id, 0),
            latest_event=latest_event_map.get(reactor.id),
            latest_vision=latest_vision_map.get(reactor.id),
            latest_health=latest_health_map.get(reactor.id),
        )
        for reactor in reactors
    ]


def _build_latest_health_map(session: Session, reactor_ids: list[int]) -> dict[int, Any]:
    from . import reactor_health as reactor_health_service

    if not reactor_ids:
        return {}
    name_map = {reactor.id: reactor.name for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()}
    latest = reactor_health_service.get_latest_for_reactors(session, reactor_ids)
    return {
        rid: reactor_health_service.to_read(assessment, reactor_name=name_map.get(rid))
        for rid, assessment in latest.items()
    }


def _build_latest_vision_map(session: Session, reactor_ids: list[int]) -> dict[int, Any]:
    from . import vision as vision_service

    if not reactor_ids:
        return {}
    result: dict[int, Any] = {}
    for reactor_id in reactor_ids:
        analysis = vision_service.get_latest_for_reactor(session, reactor_id)
        if analysis is not None:
            result[reactor_id] = vision_service.to_read(analysis)
    return result


def _build_current_charge_map(charges: list[Charge]) -> dict[int, ChargeRead]:
    charges.sort(key=lambda charge: (charge.start_date, charge.id or 0), reverse=True)
    current_charge_map: dict[int, ChargeRead] = {}
    for charge in charges:
        if charge.reactor_id is None or charge.reactor_id in current_charge_map:
            continue
        current_charge_map[charge.reactor_id] = ChargeRead.model_validate(charge)
    return current_charge_map


def _build_latest_event_map(session: Session, events: list[ReactorEvent]) -> dict[int, ReactorEventRead]:
    latest_event_map: dict[int, ReactorEventRead] = {}
    if not events:
        return latest_event_map

    serialized = _serialize_events(session, events)
    for event in serialized:
        latest_event_map.setdefault(event.reactor_id, event)
    return latest_event_map


def _serialize_events(session: Session, events: list[ReactorEvent]) -> list[ReactorEventRead]:
    if not events:
        return []

    user_ids = sorted({event.created_by_user_id for event in events if event.created_by_user_id is not None})
    reactor_ids = sorted({event.reactor_id for event in events})
    user_map = (
        {
            user.id: user.username
            for user in session.exec(select(UserAccount).where(UserAccount.id.in_(user_ids))).all()
        }
        if user_ids
        else {}
    )
    reactor_map = (
        {reactor.id: reactor.name for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()}
        if reactor_ids
        else {}
    )

    return [
        ReactorEventRead(
            id=event.id,
            reactor_id=event.reactor_id,
            reactor_name=reactor_map.get(event.reactor_id),
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            severity=event.severity,
            phase_snapshot=event.phase_snapshot,
            created_at=event.created_at,
            created_by_user_id=event.created_by_user_id,
            created_by_username=user_map.get(event.created_by_user_id),
        )
        for event in events
    ]


def _to_reactor_twin_read(
    *,
    reactor: Reactor,
    twin: ReactorTwin | None,
    current_charge: ChargeRead | None,
    sensor_count: int,
    open_task_count: int,
    open_alert_count: int,
    photo_count: int,
    latest_event: ReactorEventRead | None,
    latest_vision: Any | None = None,
    latest_health: Any | None = None,
) -> ReactorTwinRead:
    now = _utcnow()
    return ReactorTwinRead(
        id=twin.id if twin else None,
        is_configured=twin is not None,
        reactor_id=reactor.id,
        reactor_name=reactor.name,
        reactor_type=reactor.reactor_type,
        reactor_status=reactor.status,
        reactor_volume_l=reactor.volume_l,
        reactor_location=reactor.location,
        culture_type=twin.culture_type if twin else None,
        strain=twin.strain if twin else None,
        medium_recipe=twin.medium_recipe if twin else None,
        inoculated_at=twin.inoculated_at if twin else None,
        current_phase=twin.current_phase if twin else ReactorPhase.growth.value,
        target_ph_min=twin.target_ph_min if twin else None,
        target_ph_max=twin.target_ph_max if twin else None,
        target_temp_min=twin.target_temp_min if twin else None,
        target_temp_max=twin.target_temp_max if twin else None,
        target_light_min=twin.target_light_min if twin else None,
        target_light_max=twin.target_light_max if twin else None,
        target_flow_min=twin.target_flow_min if twin else None,
        target_flow_max=twin.target_flow_max if twin else None,
        expected_harvest_window_start=twin.expected_harvest_window_start if twin else None,
        expected_harvest_window_end=twin.expected_harvest_window_end if twin else None,
        contamination_state=twin.contamination_state if twin else None,
        technical_state=twin.technical_state if twin else ReactorTechnicalState.nominal.value,
        biological_state=twin.biological_state if twin else ReactorBiologicalState.unknown.value,
        notes=twin.notes if twin else None,
        created_at=twin.created_at if twin else now,
        updated_at=twin.updated_at if twin else now,
        current_charge=current_charge,
        sensor_count=sensor_count,
        open_task_count=open_task_count,
        open_alert_count=open_alert_count,
        photo_count=photo_count,
        latest_event=latest_event,
        latest_vision=latest_vision,
        latest_health=latest_health,
    )
