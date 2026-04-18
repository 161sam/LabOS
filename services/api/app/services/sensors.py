from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from ..models import Reactor, Sensor, SensorValue, _utcnow
from ..schemas import (
    SensorCreate,
    SensorOverviewRead,
    SensorRead,
    SensorStatusUpdate,
    SensorUpdate,
    SensorValueCreate,
)


def list_sensors(session: Session) -> list[SensorRead]:
    statement = select(Sensor).order_by(Sensor.name.asc(), Sensor.id.asc())
    sensors = list(session.exec(statement).all())
    return _serialize_sensors(session, sensors)


def list_sensor_overview(session: Session, limit: int = 6) -> list[SensorOverviewRead]:
    statement = select(Sensor).order_by(Sensor.name.asc(), Sensor.id.asc()).limit(limit)
    sensors = list(session.exec(statement).all())
    return [SensorOverviewRead(**sensor.model_dump()) for sensor in _serialize_sensors(session, sensors)]


def list_reactor_sensors(session: Session, reactor_id: int, limit: int | None = None) -> list[SensorRead]:
    statement = select(Sensor).where(Sensor.reactor_id == reactor_id).order_by(Sensor.name.asc(), Sensor.id.asc())
    if limit is not None:
        statement = statement.limit(limit)
    sensors = list(session.exec(statement).all())
    return _serialize_sensors(session, sensors)


def get_sensor_or_404(session: Session, sensor_id: int) -> Sensor:
    sensor = session.get(Sensor, sensor_id)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sensor not found')
    return sensor


def get_sensor_read(session: Session, sensor_id: int) -> SensorRead:
    sensor = get_sensor_or_404(session, sensor_id)
    return _serialize_sensors(session, [sensor])[0]


def create_sensor(session: Session, payload: SensorCreate) -> SensorRead:
    _validate_reactor_reference(session, payload.reactor_id)
    sensor = Sensor(
        name=payload.name,
        sensor_type=payload.sensor_type.value,
        unit=payload.unit,
        status=payload.status.value,
        reactor_id=payload.reactor_id,
        location=payload.location,
        notes=payload.notes,
    )
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return get_sensor_read(session, sensor.id)


def update_sensor(session: Session, sensor: Sensor, payload: SensorUpdate) -> SensorRead:
    _validate_reactor_reference(session, payload.reactor_id)
    sensor.name = payload.name
    sensor.sensor_type = payload.sensor_type.value
    sensor.unit = payload.unit
    sensor.status = payload.status.value
    sensor.reactor_id = payload.reactor_id
    sensor.location = payload.location
    sensor.notes = payload.notes
    sensor.updated_at = _utcnow()
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return get_sensor_read(session, sensor.id)


def update_sensor_status(session: Session, sensor: Sensor, payload: SensorStatusUpdate) -> SensorRead:
    sensor.status = payload.status.value
    sensor.updated_at = _utcnow()
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return get_sensor_read(session, sensor.id)


def create_sensor_value(session: Session, sensor: Sensor, payload: SensorValueCreate) -> SensorValue:
    sensor_value = SensorValue(
        sensor_id=sensor.id,
        value=payload.value,
        source=payload.source,
        recorded_at=payload.recorded_at or _utcnow(),
    )
    sensor.updated_at = _utcnow()
    session.add(sensor_value)
    session.add(sensor)
    session.commit()
    session.refresh(sensor_value)
    return sensor_value


def list_sensor_values(
    session: Session,
    sensor_id: int,
    limit: int = 20,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[SensorValue]:
    statement = select(SensorValue).where(SensorValue.sensor_id == sensor_id)
    if from_time is not None:
        statement = statement.where(SensorValue.recorded_at >= from_time)
    if to_time is not None:
        statement = statement.where(SensorValue.recorded_at <= to_time)

    statement = statement.order_by(SensorValue.recorded_at.desc(), SensorValue.id.desc()).limit(limit)
    return list(session.exec(statement).all())


def _serialize_sensors(session: Session, sensors: list[Sensor]) -> list[SensorRead]:
    if not sensors:
        return []

    sensor_ids = [sensor.id for sensor in sensors if sensor.id is not None]
    reactor_ids = sorted({sensor.reactor_id for sensor in sensors if sensor.reactor_id is not None})
    latest_value_map = _get_latest_value_map(session, sensor_ids)
    reactor_name_map = _get_reactor_name_map(session, reactor_ids)

    return [
        SensorRead(
            id=sensor.id,
            name=sensor.name,
            sensor_type=sensor.sensor_type,
            unit=sensor.unit,
            status=sensor.status,
            reactor_id=sensor.reactor_id,
            location=sensor.location,
            notes=sensor.notes,
            created_at=sensor.created_at,
            updated_at=sensor.updated_at,
            reactor_name=reactor_name_map.get(sensor.reactor_id),
            last_value=latest_value_map.get(sensor.id).value if latest_value_map.get(sensor.id) else None,
            last_recorded_at=latest_value_map.get(sensor.id).recorded_at if latest_value_map.get(sensor.id) else None,
            last_value_source=latest_value_map.get(sensor.id).source if latest_value_map.get(sensor.id) else None,
        )
        for sensor in sensors
    ]


def _get_latest_value_map(session: Session, sensor_ids: list[int]) -> dict[int, SensorValue]:
    if not sensor_ids:
        return {}

    latest_subquery = (
        select(
            SensorValue.sensor_id.label('sensor_id'),
            func.max(SensorValue.recorded_at).label('latest_recorded_at'),
        )
        .where(SensorValue.sensor_id.in_(sensor_ids))
        .group_by(SensorValue.sensor_id)
        .subquery()
    )

    statement = (
        select(SensorValue)
        .join(
            latest_subquery,
            (SensorValue.sensor_id == latest_subquery.c.sensor_id)
            & (SensorValue.recorded_at == latest_subquery.c.latest_recorded_at),
        )
        .order_by(SensorValue.sensor_id.asc(), SensorValue.id.desc())
    )

    latest_values: dict[int, SensorValue] = {}
    for value in session.exec(statement).all():
        latest_values.setdefault(value.sensor_id, value)
    return latest_values


def _get_reactor_name_map(session: Session, reactor_ids: list[int]) -> dict[int, str]:
    if not reactor_ids:
        return {}

    statement = select(Reactor).where(Reactor.id.in_(reactor_ids))
    return {reactor.id: reactor.name for reactor in session.exec(statement).all()}


def _validate_reactor_reference(session: Session, reactor_id: int | None) -> None:
    if reactor_id is None:
        return

    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced reactor does not exist',
        )
