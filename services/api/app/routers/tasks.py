from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..db import get_session
from ..schemas import TaskCreate, TaskPriority, TaskRead, TaskStatus, TaskStatusUpdate, TaskUpdate
from ..services import tasks as task_service

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('', response_model=list[TaskRead])
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias='status'),
    priority_filter: TaskPriority | None = Query(default=None, alias='priority'),
    session: Session = Depends(get_session),
):
    return task_service.list_tasks(session, status_filter=status_filter, priority_filter=priority_filter)


@router.get('/{task_id}', response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    return task_service.get_task_read(session, task_id)


@router.post('', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    return task_service.create_task(session, payload)


@router.put('/{task_id}', response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)):
    task = task_service.get_task_or_404(session, task_id)
    return task_service.update_task(session, task, payload)


@router.patch('/{task_id}/status', response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    session: Session = Depends(get_session),
):
    task = task_service.get_task_or_404(session, task_id)
    return task_service.update_task_status(session, task, payload)
