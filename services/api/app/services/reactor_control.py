from __future__ import annotations

from collections import defaultdict
import re
from typing import Protocol

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import DeviceNode, Reactor, ReactorCommand, ReactorSetpoint, TelemetryValue, _utcnow
from ..schemas import (
    DeviceNodeCreate,
    DeviceNodeRead,
    DeviceNodeUpdate,
    ReactorCommandCreate,
    ReactorCommandRead,
    ReactorControlParameter,
    ReactorSetpointCreate,
    ReactorSetpointRead,
    ReactorSetpointUpdate,
    ReactorTelemetryOverviewRead,
    TelemetrySensorType,
    TelemetryValueCreate,
    TelemetryValueRead,
)


class CommandPublisher(Protocol):
    def publish_reactor_command(self, *, reactor_id: int, command_id: int, command_type: str) -> bool | None:
        ...


def create_telemetry_value(session: Session, payload: TelemetryValueCreate) -> TelemetryValueRead:
    telemetry = create_telemetry_value_record(
        session,
        reactor_id=payload.reactor_id,
        sensor_type=payload.sensor_type.value,
        value=payload.value,
        unit=payload.unit,
        source=payload.source.value,
        timestamp=payload.timestamp,
    )
    session.add(telemetry)
    session.commit()
    session.refresh(telemetry)
    return _serialize_telemetry_values(session, [telemetry])[0]


def list_reactor_telemetry(
    session: Session,
    reactor_id: int,
    *,
    limit: int = 50,
    sensor_type: TelemetrySensorType | None = None,
) -> list[TelemetryValueRead]:
    get_reactor_or_404(session, reactor_id)
    statement = select(TelemetryValue).where(TelemetryValue.reactor_id == reactor_id)
    if sensor_type is not None:
        statement = statement.where(TelemetryValue.sensor_type == sensor_type.value)
    statement = statement.order_by(TelemetryValue.timestamp.desc(), TelemetryValue.id.desc()).limit(limit)
    values = list(session.exec(statement).all())
    return _serialize_telemetry_values(session, values)


def list_reactor_latest_telemetry(session: Session, reactor_id: int) -> list[TelemetryValueRead]:
    get_reactor_or_404(session, reactor_id)
    values = list(
        session.exec(
            select(TelemetryValue)
            .where(TelemetryValue.reactor_id == reactor_id)
            .order_by(TelemetryValue.timestamp.desc(), TelemetryValue.id.desc())
        ).all()
    )
    latest_by_sensor_type: dict[str, TelemetryValue] = {}
    for value in values:
        latest_by_sensor_type.setdefault(value.sensor_type, value)
    latest_values = sorted(
        latest_by_sensor_type.values(),
        key=lambda item: (item.timestamp, item.id or 0),
        reverse=True,
    )
    return _serialize_telemetry_values(session, latest_values)


def list_devices(session: Session) -> list[DeviceNodeRead]:
    devices = list(session.exec(select(DeviceNode).order_by(DeviceNode.name.asc(), DeviceNode.id.asc())).all())
    return _serialize_devices(session, devices)


def create_device(session: Session, payload: DeviceNodeCreate) -> DeviceNodeRead:
    _validate_optional_reactor(session, payload.reactor_id)
    node_id = payload.node_id or _derive_node_id(payload.name)
    _validate_unique_node_id(session, node_id)
    device = DeviceNode(
        name=payload.name,
        node_id=node_id,
        node_type=payload.node_type.value,
        status=payload.status.value,
        last_seen_at=payload.last_seen_at or _utcnow(),
        firmware_version=payload.firmware_version,
        reactor_id=payload.reactor_id,
    )
    session.add(device)
    session.commit()
    session.refresh(device)
    return _serialize_devices(session, [device])[0]


def update_device(session: Session, device_id: int, payload: DeviceNodeUpdate) -> DeviceNodeRead:
    device = get_device_or_404(session, device_id)
    if 'node_id' in payload.model_fields_set:
        normalized_node_id = payload.node_id or None
        if normalized_node_id is not None:
            _validate_unique_node_id(session, normalized_node_id, exclude_device_id=device.id)
        device.node_id = normalized_node_id
    if 'status' in payload.model_fields_set and payload.status is not None:
        device.status = payload.status.value
    if 'last_seen_at' in payload.model_fields_set:
        device.last_seen_at = payload.last_seen_at or _utcnow()
    if 'firmware_version' in payload.model_fields_set:
        device.firmware_version = payload.firmware_version
    if 'reactor_id' in payload.model_fields_set:
        _validate_optional_reactor(session, payload.reactor_id)
        device.reactor_id = payload.reactor_id
    device.updated_at = _utcnow()
    session.add(device)
    session.commit()
    session.refresh(device)
    return _serialize_devices(session, [device])[0]


def list_reactor_setpoints(session: Session, reactor_id: int) -> list[ReactorSetpointRead]:
    get_reactor_or_404(session, reactor_id)
    setpoints = list(
        session.exec(
            select(ReactorSetpoint)
            .where(ReactorSetpoint.reactor_id == reactor_id)
            .order_by(ReactorSetpoint.parameter.asc(), ReactorSetpoint.id.asc())
        ).all()
    )
    return _serialize_setpoints(session, setpoints)


def create_reactor_setpoint(
    session: Session,
    reactor_id: int,
    payload: ReactorSetpointCreate,
) -> ReactorSetpointRead:
    get_reactor_or_404(session, reactor_id)
    existing = session.exec(
        select(ReactorSetpoint).where(
            ReactorSetpoint.reactor_id == reactor_id,
            ReactorSetpoint.parameter == payload.parameter.value,
        )
    ).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Setpoint for parameter already exists')

    setpoint = ReactorSetpoint(
        reactor_id=reactor_id,
        parameter=payload.parameter.value,
        target_value=payload.target_value,
        min_value=payload.min_value,
        max_value=payload.max_value,
        mode=payload.mode.value,
        updated_at=_utcnow(),
    )
    session.add(setpoint)
    session.commit()
    session.refresh(setpoint)
    return _serialize_setpoints(session, [setpoint])[0]


def update_reactor_setpoint(
    session: Session,
    setpoint_id: int,
    payload: ReactorSetpointUpdate,
) -> ReactorSetpointRead:
    setpoint = get_setpoint_or_404(session, setpoint_id)
    if 'target_value' in payload.model_fields_set and payload.target_value is not None:
        setpoint.target_value = payload.target_value
    if 'min_value' in payload.model_fields_set:
        setpoint.min_value = payload.min_value
    if 'max_value' in payload.model_fields_set:
        setpoint.max_value = payload.max_value
    if 'mode' in payload.model_fields_set and payload.mode is not None:
        setpoint.mode = payload.mode.value
    setpoint.updated_at = _utcnow()
    session.add(setpoint)
    session.commit()
    session.refresh(setpoint)
    return _serialize_setpoints(session, [setpoint])[0]


def list_reactor_commands(session: Session, reactor_id: int) -> list[ReactorCommandRead]:
    get_reactor_or_404(session, reactor_id)
    commands = list(
        session.exec(
            select(ReactorCommand)
            .where(ReactorCommand.reactor_id == reactor_id)
            .order_by(ReactorCommand.created_at.desc(), ReactorCommand.id.desc())
        ).all()
    )
    return _serialize_commands(session, commands)


def create_reactor_command(
    session: Session,
    reactor_id: int,
    payload: ReactorCommandCreate,
    *,
    publisher: CommandPublisher | None = None,
) -> ReactorCommandRead:
    from . import safety as safety_service
    get_reactor_or_404(session, reactor_id)
    blocked_reason = safety_service.check_command_guards(session, reactor_id, payload.command_type.value)
    if blocked_reason is not None:
        command = ReactorCommand(
            reactor_id=reactor_id,
            command_type=payload.command_type.value,
            status='blocked',
            blocked_reason=blocked_reason,
        )
        session.add(command)
        session.commit()
        session.refresh(command)
        return _serialize_commands(session, [command])[0]
    command = ReactorCommand(
        reactor_id=reactor_id,
        command_type=payload.command_type.value,
        status='pending',
    )
    session.add(command)
    session.commit()
    session.refresh(command)
    if publisher is not None:
        publish_result = publisher.publish_reactor_command(
            reactor_id=reactor_id,
            command_id=command.id,
            command_type=command.command_type,
        )
        if publish_result is True:
            command.status = 'sent'
        elif publish_result is False:
            command.status = 'failed'
        session.add(command)
        session.commit()
        session.refresh(command)
    return _serialize_commands(session, [command])[0]


def count_offline_devices(session: Session) -> int:
    return len(session.exec(select(DeviceNode.id).where(DeviceNode.status == 'offline')).all())


def list_reactor_telemetry_overview(session: Session) -> list[ReactorTelemetryOverviewRead]:
    reactors = list(session.exec(select(Reactor).order_by(Reactor.name.asc(), Reactor.id.asc())).all())
    telemetry_values = list(
        session.exec(
            select(TelemetryValue).order_by(TelemetryValue.timestamp.desc(), TelemetryValue.id.desc())
        ).all()
    )
    values_by_reactor: dict[int, dict[str, TelemetryValue]] = defaultdict(dict)
    last_timestamp_by_reactor: dict[int, object] = {}
    for value in telemetry_values:
        if value.reactor_id not in last_timestamp_by_reactor:
            last_timestamp_by_reactor[value.reactor_id] = value.timestamp
        values_by_reactor[value.reactor_id].setdefault(value.sensor_type, value)

    overview: list[ReactorTelemetryOverviewRead] = []
    for reactor in reactors:
        reactor_values = values_by_reactor.get(reactor.id, {})
        temp_value = reactor_values.get(ReactorControlParameter.temp.value)
        ph_value = reactor_values.get(ReactorControlParameter.ph.value)
        overview.append(
            ReactorTelemetryOverviewRead(
                reactor_id=reactor.id,
                reactor_name=reactor.name,
                latest_temp=temp_value.value if temp_value else None,
                latest_temp_unit=temp_value.unit if temp_value else None,
                latest_ph=ph_value.value if ph_value else None,
                latest_ph_unit=ph_value.unit if ph_value else None,
                last_telemetry_at=last_timestamp_by_reactor.get(reactor.id),
            )
        )
    return overview


def get_reactor_or_404(session: Session, reactor_id: int) -> Reactor:
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    return reactor


def get_device_or_404(session: Session, device_id: int) -> DeviceNode:
    device = session.get(DeviceNode, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Device not found')
    return device


def get_setpoint_or_404(session: Session, setpoint_id: int) -> ReactorSetpoint:
    setpoint = session.get(ReactorSetpoint, setpoint_id)
    if setpoint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Setpoint not found')
    return setpoint


def _validate_optional_reactor(session: Session, reactor_id: int | None) -> None:
    if reactor_id is None:
        return
    get_reactor_or_404(session, reactor_id)


def create_telemetry_value_record(
    session: Session,
    *,
    reactor_id: int,
    sensor_type: str,
    value: float,
    unit: str,
    source: str,
    timestamp=None,
) -> TelemetryValue:
    reactor = get_reactor_or_404(session, reactor_id)
    return TelemetryValue(
        reactor_id=reactor.id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        source=source,
        timestamp=timestamp or _utcnow(),
    )


def upsert_device_node_by_node_id(
    session: Session,
    *,
    node_id: str,
    name: str,
    node_type: str,
    status: str,
    last_seen_at=None,
    firmware_version: str | None = None,
    reactor_id: int | None = None,
) -> DeviceNode:
    _validate_optional_reactor(session, reactor_id)
    device = session.exec(select(DeviceNode).where(DeviceNode.node_id == node_id)).first()
    if device is None:
        device = DeviceNode(
            name=name,
            node_id=node_id,
            node_type=node_type,
            status=status,
            last_seen_at=last_seen_at or _utcnow(),
            firmware_version=firmware_version,
            reactor_id=reactor_id,
        )
    else:
        device.name = name or device.name
        device.node_type = node_type
        device.status = status
        device.last_seen_at = last_seen_at or _utcnow()
        if firmware_version is not None:
            device.firmware_version = firmware_version
        if reactor_id is not None or device.reactor_id is None:
            device.reactor_id = reactor_id
        device.updated_at = _utcnow()
    session.add(device)
    return device


def _validate_unique_node_id(session: Session, node_id: str, *, exclude_device_id: int | None = None) -> None:
    existing = session.exec(select(DeviceNode).where(DeviceNode.node_id == node_id)).first()
    if existing is None:
        return
    if exclude_device_id is not None and existing.id == exclude_device_id:
        return
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Device node_id already exists')


def _derive_node_id(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug or 'device-node'


def _serialize_telemetry_values(session: Session, values: list[TelemetryValue]) -> list[TelemetryValueRead]:
    if not values:
        return []
    reactor_ids = sorted({value.reactor_id for value in values})
    reactor_map = {
        reactor.id: reactor.name
        for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    return [
        TelemetryValueRead(
            id=value.id,
            reactor_id=value.reactor_id,
            reactor_name=reactor_map.get(value.reactor_id),
            sensor_type=value.sensor_type,
            value=value.value,
            unit=value.unit,
            source=value.source,
            timestamp=value.timestamp,
            created_at=value.created_at,
        )
        for value in values
    ]


def _serialize_devices(session: Session, devices: list[DeviceNode]) -> list[DeviceNodeRead]:
    if not devices:
        return []
    reactor_ids = sorted({device.reactor_id for device in devices if device.reactor_id is not None})
    reactor_map = {
        reactor.id: reactor.name
        for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    return [
        DeviceNodeRead(
            id=device.id,
            name=device.name,
            node_id=device.node_id,
            node_type=device.node_type,
            status=device.status,
            last_seen_at=device.last_seen_at,
            firmware_version=device.firmware_version,
            reactor_id=device.reactor_id,
            reactor_name=reactor_map.get(device.reactor_id),
            created_at=device.created_at,
            updated_at=device.updated_at,
        )
        for device in devices
    ]


def _serialize_setpoints(session: Session, setpoints: list[ReactorSetpoint]) -> list[ReactorSetpointRead]:
    if not setpoints:
        return []
    reactor_ids = sorted({setpoint.reactor_id for setpoint in setpoints})
    reactor_map = {
        reactor.id: reactor.name
        for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    return [
        ReactorSetpointRead(
            id=setpoint.id,
            reactor_id=setpoint.reactor_id,
            reactor_name=reactor_map.get(setpoint.reactor_id),
            parameter=setpoint.parameter,
            target_value=setpoint.target_value,
            min_value=setpoint.min_value,
            max_value=setpoint.max_value,
            mode=setpoint.mode,
            updated_at=setpoint.updated_at,
        )
        for setpoint in setpoints
    ]


def _serialize_commands(session: Session, commands: list[ReactorCommand]) -> list[ReactorCommandRead]:
    if not commands:
        return []
    reactor_ids = sorted({command.reactor_id for command in commands})
    reactor_map = {
        reactor.id: reactor.name
        for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    return [
        ReactorCommandRead(
            id=command.id,
            reactor_id=command.reactor_id,
            reactor_name=reactor_map.get(command.reactor_id),
            command_type=command.command_type,
            status=command.status,
            blocked_reason=command.blocked_reason,
            created_at=command.created_at,
        )
        for command in commands
    ]
