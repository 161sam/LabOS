from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Asset, Charge, Reactor, Task, _utcnow
from ..schemas import TaskCreate, TaskPriority, TaskRead, TaskStatus, TaskStatusUpdate, TaskUpdate

_TASK_PRIORITY_ORDER = {
    TaskPriority.critical.value: 0,
    TaskPriority.high.value: 1,
    TaskPriority.normal.value: 2,
    TaskPriority.low.value: 3,
}


def list_tasks(
    session: Session,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
    asset_id: int | None = None,
) -> list[TaskRead]:
    statement = select(Task)
    if status_filter is not None:
        statement = statement.where(Task.status == status_filter.value)
    if priority_filter is not None:
        statement = statement.where(Task.priority == priority_filter.value)
    if asset_id is not None:
        statement = statement.where(Task.asset_id == asset_id)

    tasks = list(session.exec(statement).all())
    tasks.sort(
        key=lambda task: (
            _TASK_PRIORITY_ORDER.get(task.priority, 99),
            task.due_at or datetime.max,
            task.id or 0,
        )
    )
    return _serialize_tasks(session, tasks)


def get_task_or_404(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    return task


def get_task_read(session: Session, task_id: int) -> TaskRead:
    task = get_task_or_404(session, task_id)
    return _serialize_tasks(session, [task])[0]


def create_task(session: Session, payload: TaskCreate) -> TaskRead:
    _validate_references(session, payload.charge_id, payload.reactor_id, payload.asset_id)
    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status.value,
        priority=payload.priority.value,
        due_at=payload.due_at,
        charge_id=payload.charge_id,
        reactor_id=payload.reactor_id,
        asset_id=payload.asset_id,
    )
    _apply_completion(task, payload.status.value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return get_task_read(session, task.id)


def update_task(session: Session, task: Task, payload: TaskUpdate) -> TaskRead:
    _validate_references(session, payload.charge_id, payload.reactor_id, payload.asset_id)
    task.title = payload.title
    task.description = payload.description
    task.status = payload.status.value
    task.priority = payload.priority.value
    task.due_at = payload.due_at
    task.charge_id = payload.charge_id
    task.reactor_id = payload.reactor_id
    task.asset_id = payload.asset_id
    task.updated_at = _utcnow()
    _apply_completion(task, payload.status.value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return get_task_read(session, task.id)


def update_task_status(session: Session, task: Task, payload: TaskStatusUpdate) -> TaskRead:
    task.status = payload.status.value
    task.updated_at = _utcnow()
    _apply_completion(task, payload.status.value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return get_task_read(session, task.id)


def _apply_completion(task: Task, status_value: str) -> None:
    if status_value == TaskStatus.done.value:
        task.completed_at = task.completed_at or _utcnow()
    else:
        task.completed_at = None


def _serialize_tasks(session: Session, tasks: list[Task]) -> list[TaskRead]:
    if not tasks:
        return []

    charge_ids = sorted({task.charge_id for task in tasks if task.charge_id is not None})
    reactor_ids = sorted({task.reactor_id for task in tasks if task.reactor_id is not None})
    asset_ids = sorted({task.asset_id for task in tasks if task.asset_id is not None})
    charges = {
        charge.id: charge.name
        for charge in session.exec(select(Charge).where(Charge.id.in_(charge_ids))).all()
    } if charge_ids else {}
    reactors = {
        reactor.id: reactor.name
        for reactor in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    assets = {
        asset.id: asset.name
        for asset in session.exec(select(Asset).where(Asset.id.in_(asset_ids))).all()
    } if asset_ids else {}

    return [
        TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            charge_id=task.charge_id,
            reactor_id=task.reactor_id,
            asset_id=task.asset_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            charge_name=charges.get(task.charge_id),
            reactor_name=reactors.get(task.reactor_id),
            asset_name=assets.get(task.asset_id),
        )
        for task in tasks
    ]


def _validate_references(
    session: Session,
    charge_id: int | None,
    reactor_id: int | None,
    asset_id: int | None,
) -> None:
    if charge_id is not None and session.get(Charge, charge_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced charge does not exist',
        )
    if reactor_id is not None and session.get(Reactor, reactor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced reactor does not exist',
        )
    if asset_id is not None and session.get(Asset, asset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Referenced asset does not exist',
        )
