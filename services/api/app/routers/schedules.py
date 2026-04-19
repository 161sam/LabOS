from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    ScheduleCreate,
    ScheduleEnabledUpdate,
    ScheduleExecutionRead,
    ScheduleRead,
    ScheduleRunResponse,
    ScheduleUpdate,
)
from ..services import scheduler as scheduler_service

router = APIRouter(
    prefix='/schedules',
    tags=['schedules'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[ScheduleRead])
def list_schedules(session: Session = Depends(get_session)):
    return scheduler_service.list_schedules(session)


@router.post('', response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    session: Session = Depends(get_session),
    _=Depends(require_operator_user),
):
    return scheduler_service.create_schedule(session, payload)


@router.get('/{schedule_id}', response_model=ScheduleRead)
def get_schedule(schedule_id: int, session: Session = Depends(get_session)):
    schedule = scheduler_service.get_schedule_or_404(session, schedule_id)
    return scheduler_service._serialize_schedule(schedule)


@router.patch('/{schedule_id}', response_model=ScheduleRead)
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    session: Session = Depends(get_session),
    _=Depends(require_operator_user),
):
    return scheduler_service.update_schedule(session, schedule_id, payload)


@router.patch('/{schedule_id}/enabled', response_model=ScheduleRead)
def set_schedule_enabled(
    schedule_id: int,
    payload: ScheduleEnabledUpdate,
    session: Session = Depends(get_session),
    _=Depends(require_operator_user),
):
    return scheduler_service.set_schedule_enabled(session, schedule_id, enabled=payload.is_enabled)


@router.delete('/{schedule_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    session: Session = Depends(get_session),
    _=Depends(require_operator_user),
):
    scheduler_service.delete_schedule(session, schedule_id)


@router.get('/{schedule_id}/executions', response_model=list[ScheduleExecutionRead])
def list_schedule_executions(
    schedule_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    return scheduler_service.list_schedule_executions(session, schedule_id, limit=limit)


@router.post('/{schedule_id}/run', response_model=ScheduleRunResponse)
def run_schedule_now(
    schedule_id: int,
    session: Session = Depends(get_session),
    _=Depends(require_operator_user),
):
    schedule, execution = scheduler_service.run_schedule_now(session, schedule_id)
    return ScheduleRunResponse(schedule=schedule, execution=execution)
