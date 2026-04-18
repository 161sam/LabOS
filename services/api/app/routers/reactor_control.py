from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    DeviceNodeCreate,
    DeviceNodeRead,
    DeviceNodeUpdate,
    ReactorCommandCreate,
    ReactorCommandRead,
    ReactorSetpointCreate,
    ReactorSetpointRead,
    ReactorSetpointUpdate,
    TelemetrySensorType,
    TelemetryValueCreate,
    TelemetryValueRead,
)
from ..services import reactor_control as reactor_control_service

router = APIRouter(tags=['reactor-control'], dependencies=[Depends(require_authenticated_user)])


@router.post('/telemetry', response_model=TelemetryValueRead, status_code=status.HTTP_201_CREATED)
def create_telemetry_value(
    payload: TelemetryValueCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.create_telemetry_value(session, payload)


@router.get('/reactors/{reactor_id}/telemetry', response_model=list[TelemetryValueRead])
def list_reactor_telemetry(
    reactor_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    sensor_type: TelemetrySensorType | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return reactor_control_service.list_reactor_telemetry(
        session,
        reactor_id=reactor_id,
        limit=limit,
        sensor_type=sensor_type,
    )


@router.get('/reactors/{reactor_id}/telemetry/latest', response_model=list[TelemetryValueRead])
def list_reactor_latest_telemetry(reactor_id: int, session: Session = Depends(get_session)):
    return reactor_control_service.list_reactor_latest_telemetry(session, reactor_id=reactor_id)


@router.get('/devices', response_model=list[DeviceNodeRead])
def list_devices(session: Session = Depends(get_session)):
    return reactor_control_service.list_devices(session)


@router.post('/devices', response_model=DeviceNodeRead, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceNodeCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.create_device(session, payload)


@router.patch('/devices/{device_id}', response_model=DeviceNodeRead)
def update_device(
    device_id: int,
    payload: DeviceNodeUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.update_device(session, device_id=device_id, payload=payload)


@router.get('/reactors/{reactor_id}/setpoints', response_model=list[ReactorSetpointRead])
def list_reactor_setpoints(reactor_id: int, session: Session = Depends(get_session)):
    return reactor_control_service.list_reactor_setpoints(session, reactor_id=reactor_id)


@router.post('/reactors/{reactor_id}/setpoints', response_model=ReactorSetpointRead, status_code=status.HTTP_201_CREATED)
def create_reactor_setpoint(
    reactor_id: int,
    payload: ReactorSetpointCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.create_reactor_setpoint(session, reactor_id=reactor_id, payload=payload)


@router.patch('/setpoints/{setpoint_id}', response_model=ReactorSetpointRead)
def update_reactor_setpoint(
    setpoint_id: int,
    payload: ReactorSetpointUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.update_reactor_setpoint(session, setpoint_id=setpoint_id, payload=payload)


@router.post('/reactors/{reactor_id}/commands', response_model=ReactorCommandRead, status_code=status.HTTP_201_CREATED)
def create_reactor_command(
    reactor_id: int,
    payload: ReactorCommandCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_control_service.create_reactor_command(session, reactor_id=reactor_id, payload=payload)


@router.get('/reactors/{reactor_id}/commands', response_model=list[ReactorCommandRead])
def list_reactor_commands(reactor_id: int, session: Session = Depends(get_session)):
    return reactor_control_service.list_reactor_commands(session, reactor_id=reactor_id)
