from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    SensorCreate,
    SensorOverviewRead,
    SensorRead,
    SensorStatusUpdate,
    SensorUpdate,
    SensorValueCreate,
    SensorValueRead,
)
from ..services import sensors as sensor_service

router = APIRouter(
    prefix='/sensors',
    tags=['sensors'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[SensorRead])
def list_sensors(session: Session = Depends(get_session)):
    return sensor_service.list_sensors(session)


@router.get('/overview', response_model=list[SensorOverviewRead])
def sensor_overview(
    limit: int = Query(default=6, ge=1, le=20),
    session: Session = Depends(get_session),
):
    return sensor_service.list_sensor_overview(session, limit=limit)


@router.get('/{sensor_id}', response_model=SensorRead)
def get_sensor(sensor_id: int, session: Session = Depends(get_session)):
    return sensor_service.get_sensor_read(session, sensor_id)


@router.post(
    '',
    response_model=SensorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
def create_sensor(payload: SensorCreate, session: Session = Depends(get_session)):
    return sensor_service.create_sensor(session, payload)


@router.put(
    '/{sensor_id}',
    response_model=SensorRead,
    dependencies=[Depends(require_operator_user)],
)
def update_sensor(sensor_id: int, payload: SensorUpdate, session: Session = Depends(get_session)):
    sensor = sensor_service.get_sensor_or_404(session, sensor_id)
    return sensor_service.update_sensor(session, sensor, payload)


@router.patch(
    '/{sensor_id}/status',
    response_model=SensorRead,
    dependencies=[Depends(require_operator_user)],
)
def update_sensor_status(
    sensor_id: int,
    payload: SensorStatusUpdate,
    session: Session = Depends(get_session),
):
    sensor = sensor_service.get_sensor_or_404(session, sensor_id)
    return sensor_service.update_sensor_status(session, sensor, payload)


@router.post(
    '/{sensor_id}/values',
    response_model=SensorValueRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
def create_sensor_value(
    sensor_id: int,
    payload: SensorValueCreate,
    session: Session = Depends(get_session),
):
    sensor = sensor_service.get_sensor_or_404(session, sensor_id)
    return sensor_service.create_sensor_value(session, sensor, payload)


@router.get('/{sensor_id}/values', response_model=list[SensorValueRead])
def list_sensor_values(
    sensor_id: int,
    limit: int = Query(default=20, ge=1, le=200),
    from_time: datetime | None = Query(default=None, alias='from'),
    to_time: datetime | None = Query(default=None, alias='to'),
    session: Session = Depends(get_session),
):
    sensor_service.get_sensor_or_404(session, sensor_id)
    return sensor_service.list_sensor_values(
        session,
        sensor_id=sensor_id,
        limit=limit,
        from_time=from_time,
        to_time=to_time,
    )
