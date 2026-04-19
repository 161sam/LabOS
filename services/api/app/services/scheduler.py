from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta
from typing import Callable

from fastapi import HTTPException, status
from sqlmodel import Session, select

from .. import db as db_module
from ..config import settings
from ..models import Rule, Schedule, ScheduleExecution, _utcnow
from ..schemas import (
    ReactorCommandCreate,
    ReactorCommandType,
    ScheduleCreate,
    ScheduleExecutionRead,
    ScheduleExecutionStatus,
    ScheduleRead,
    ScheduleTargetType,
    ScheduleType,
    ScheduleUpdate,
)
from . import reactor_control as reactor_control_service
from . import rules as rules_service

logger = logging.getLogger(__name__)

MAX_EXECUTIONS_PER_SCHEDULE = 100


def _serialize_schedule(schedule: Schedule) -> ScheduleRead:
    return ScheduleRead.model_validate(schedule)


def _serialize_execution(execution: ScheduleExecution) -> ScheduleExecutionRead:
    return ScheduleExecutionRead.model_validate(execution)


def compute_next_run(schedule: Schedule, *, after: datetime | None = None) -> datetime | None:
    reference = after or _utcnow()
    if schedule.schedule_type == ScheduleType.manual.value:
        return None
    if schedule.schedule_type == ScheduleType.interval.value:
        if not schedule.interval_seconds:
            return None
        return reference + timedelta(seconds=schedule.interval_seconds)
    if schedule.schedule_type == ScheduleType.cron.value:
        return _compute_next_cron(schedule.cron_expr or '', reference)
    return None


def _compute_next_cron(expr: str, reference: datetime) -> datetime | None:
    fields = expr.strip().split()
    if len(fields) != 5:
        return None
    try:
        minutes = _parse_cron_field(fields[0], 0, 59)
        hours = _parse_cron_field(fields[1], 0, 23)
        days = _parse_cron_field(fields[2], 1, 31)
        months = _parse_cron_field(fields[3], 1, 12)
        dows = _parse_cron_field(fields[4], 0, 6)
    except ValueError:
        return None
    candidate = reference.replace(second=0, microsecond=0) + timedelta(minutes=1)
    for _ in range(60 * 24 * 366):
        if (
            candidate.minute in minutes
            and candidate.hour in hours
            and candidate.day in days
            and candidate.month in months
            and (candidate.weekday() + 1) % 7 in dows
        ):
            return candidate
        candidate = candidate + timedelta(minutes=1)
    return None


def _parse_cron_field(field: str, min_value: int, max_value: int) -> set[int]:
    if field == '*':
        return set(range(min_value, max_value + 1))
    result: set[int] = set()
    for part in field.split(','):
        if '/' in part:
            base, step_str = part.split('/', 1)
            step = int(step_str)
            if base == '*':
                start, end = min_value, max_value
            elif '-' in base:
                start_str, end_str = base.split('-', 1)
                start, end = int(start_str), int(end_str)
            else:
                start, end = int(base), max_value
            for value in range(start, end + 1, step):
                if min_value <= value <= max_value:
                    result.add(value)
        elif '-' in part:
            start_str, end_str = part.split('-', 1)
            for value in range(int(start_str), int(end_str) + 1):
                if min_value <= value <= max_value:
                    result.add(value)
        else:
            value = int(part)
            if min_value <= value <= max_value:
                result.add(value)
    if not result:
        raise ValueError(f'empty cron field: {field}')
    return result


def validate_cron_expr(expr: str) -> None:
    result = _compute_next_cron(expr, _utcnow())
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'invalid cron expression: {expr!r}',
        )


def list_schedules(session: Session) -> list[ScheduleRead]:
    schedules = session.exec(
        select(Schedule).order_by(Schedule.created_at.desc(), Schedule.id.desc())
    ).all()
    return [_serialize_schedule(s) for s in schedules]


def get_schedule_or_404(session: Session, schedule_id: int) -> Schedule:
    schedule = session.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Schedule not found')
    return schedule


def create_schedule(session: Session, payload: ScheduleCreate) -> ScheduleRead:
    if payload.schedule_type == ScheduleType.cron:
        validate_cron_expr(payload.cron_expr or '')
    if payload.target_type == ScheduleTargetType.command:
        _validate_command_schedule(payload.target_params, payload.reactor_id)
    if payload.target_type == ScheduleTargetType.rule and payload.target_id is not None:
        rules_service.get_rule_or_404(session, payload.target_id)

    schedule = Schedule(
        name=payload.name,
        description=payload.description,
        schedule_type=payload.schedule_type.value,
        interval_seconds=payload.interval_seconds,
        cron_expr=payload.cron_expr,
        target_type=payload.target_type.value,
        target_id=payload.target_id,
        reactor_id=payload.reactor_id,
        target_params=dict(payload.target_params or {}),
        is_enabled=payload.is_enabled,
    )
    schedule.next_run_at = compute_next_run(schedule) if schedule.is_enabled else None
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return _serialize_schedule(schedule)


def update_schedule(session: Session, schedule_id: int, payload: ScheduleUpdate) -> ScheduleRead:
    schedule = get_schedule_or_404(session, schedule_id)
    if payload.schedule_type == ScheduleType.cron:
        validate_cron_expr(payload.cron_expr or '')
    if payload.target_type == ScheduleTargetType.command:
        _validate_command_schedule(payload.target_params, payload.reactor_id)
    if payload.target_type == ScheduleTargetType.rule and payload.target_id is not None:
        rules_service.get_rule_or_404(session, payload.target_id)

    schedule.name = payload.name
    schedule.description = payload.description
    schedule.schedule_type = payload.schedule_type.value
    schedule.interval_seconds = payload.interval_seconds
    schedule.cron_expr = payload.cron_expr
    schedule.target_type = payload.target_type.value
    schedule.target_id = payload.target_id
    schedule.reactor_id = payload.reactor_id
    schedule.target_params = dict(payload.target_params or {})
    schedule.is_enabled = payload.is_enabled
    schedule.updated_at = _utcnow()
    schedule.next_run_at = compute_next_run(schedule) if schedule.is_enabled else None
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return _serialize_schedule(schedule)


def set_schedule_enabled(session: Session, schedule_id: int, *, enabled: bool) -> ScheduleRead:
    schedule = get_schedule_or_404(session, schedule_id)
    schedule.is_enabled = enabled
    schedule.updated_at = _utcnow()
    schedule.next_run_at = compute_next_run(schedule) if enabled else None
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return _serialize_schedule(schedule)


def delete_schedule(session: Session, schedule_id: int) -> None:
    schedule = get_schedule_or_404(session, schedule_id)
    executions = session.exec(
        select(ScheduleExecution).where(ScheduleExecution.schedule_id == schedule.id)
    ).all()
    for execution in executions:
        session.delete(execution)
    session.delete(schedule)
    session.commit()


def list_schedule_executions(session: Session, schedule_id: int, *, limit: int = 50) -> list[ScheduleExecutionRead]:
    get_schedule_or_404(session, schedule_id)
    executions = session.exec(
        select(ScheduleExecution)
        .where(ScheduleExecution.schedule_id == schedule_id)
        .order_by(ScheduleExecution.started_at.desc(), ScheduleExecution.id.desc())
        .limit(limit)
    ).all()
    return [_serialize_execution(e) for e in executions]


def find_due_schedules(session: Session, *, now: datetime | None = None) -> list[Schedule]:
    reference = now or _utcnow()
    return list(
        session.exec(
            select(Schedule)
            .where(Schedule.is_enabled.is_(True))
            .where(Schedule.next_run_at.is_not(None))
            .where(Schedule.next_run_at <= reference)
        ).all()
    )


def execute_schedule(
    session: Session,
    schedule: Schedule,
    *,
    trigger: str = 'scheduler',
) -> ScheduleExecution:
    started = _utcnow()
    execution = ScheduleExecution(
        schedule_id=schedule.id,
        status=ScheduleExecutionStatus.success.value,
        trigger=trigger,
        started_at=started,
        result={},
    )
    try:
        result = _dispatch_schedule(session, schedule)
        execution.result = result
        execution.status = ScheduleExecutionStatus.success.value
        schedule.last_status = ScheduleExecutionStatus.success.value
        schedule.last_error = None
    except Exception as exc:  # pragma: no cover - defensive; message captured for UI
        logger.exception('schedule %s execution failed', schedule.id)
        execution.status = ScheduleExecutionStatus.failed.value
        execution.error = str(exc)
        execution.result = {'executed': False, 'error': str(exc)}
        schedule.last_status = ScheduleExecutionStatus.failed.value
        schedule.last_error = str(exc)

    finished = _utcnow()
    execution.finished_at = finished
    schedule.last_run_at = finished
    schedule.next_run_at = compute_next_run(schedule, after=finished) if schedule.is_enabled else None
    schedule.updated_at = finished
    session.add(execution)
    session.add(schedule)
    session.commit()
    session.refresh(execution)
    session.refresh(schedule)
    _prune_executions(session, schedule.id)
    return execution


def run_schedule_now(session: Session, schedule_id: int) -> tuple[ScheduleRead, ScheduleExecutionRead]:
    schedule = get_schedule_or_404(session, schedule_id)
    execution = execute_schedule(session, schedule, trigger='manual')
    session.refresh(schedule)
    return _serialize_schedule(schedule), _serialize_execution(execution)


def tick(session: Session, *, now: datetime | None = None) -> list[ScheduleExecution]:
    reference = now or _utcnow()
    executions: list[ScheduleExecution] = []
    for schedule in find_due_schedules(session, now=reference):
        try:
            executions.append(execute_schedule(session, schedule, trigger='scheduler'))
        except Exception:  # pragma: no cover - executor handles per-schedule errors itself
            logger.exception('scheduler tick failed for schedule %s', schedule.id)
    return executions


def _validate_command_schedule(target_params: dict, reactor_id: int | None) -> None:
    command_type = (target_params or {}).get('command_type')
    if not command_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='command schedules require target_params.command_type',
        )
    try:
        ReactorCommandType(command_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'invalid command_type: {command_type}',
        ) from exc
    if reactor_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='command schedules require reactor_id',
        )


def _dispatch_schedule(session: Session, schedule: Schedule) -> dict:
    if schedule.target_type == ScheduleTargetType.command.value:
        command_type = (schedule.target_params or {}).get('command_type')
        if not command_type:
            raise ValueError('schedule missing command_type')
        if schedule.reactor_id is None:
            raise ValueError('schedule missing reactor_id')
        payload = ReactorCommandCreate(command_type=ReactorCommandType(command_type))
        from .mqtt_bridge import get_mqtt_bridge
        publisher = get_mqtt_bridge()
        command = reactor_control_service.create_reactor_command(
            session,
            reactor_id=schedule.reactor_id,
            payload=payload,
            publisher=publisher,
        )
        return {
            'executed': True,
            'action': 'command',
            'command_id': command.id,
            'command_status': command.status.value if hasattr(command.status, 'value') else command.status,
            'command_type': command_type,
            'reactor_id': schedule.reactor_id,
            'blocked_reason': command.blocked_reason,
        }
    if schedule.target_type == ScheduleTargetType.rule.value:
        if schedule.target_id is None:
            raise ValueError('rule schedule missing target_id')
        rule = rules_service.get_rule_or_404(session, schedule.target_id)
        dry_run = bool((schedule.target_params or {}).get('dry_run', False))
        response = rules_service.evaluate_rule(session, rule, dry_run=dry_run)
        return {
            'executed': True,
            'action': 'rule',
            'rule_id': schedule.target_id,
            'dry_run': dry_run,
            'execution_status': response.execution.status.value
            if hasattr(response.execution.status, 'value')
            else response.execution.status,
        }
    raise ValueError(f'unsupported target_type: {schedule.target_type}')


def _prune_executions(session: Session, schedule_id: int) -> None:
    executions = session.exec(
        select(ScheduleExecution)
        .where(ScheduleExecution.schedule_id == schedule_id)
        .order_by(ScheduleExecution.started_at.desc(), ScheduleExecution.id.desc())
    ).all()
    if len(executions) <= MAX_EXECUTIONS_PER_SCHEDULE:
        return
    for execution in executions[MAX_EXECUTIONS_PER_SCHEDULE:]:
        session.delete(execution)
    session.commit()


class SchedulerRunner:
    def __init__(self, session_factory: Callable[[], Session] | None = None):
        self._session_factory = session_factory or (lambda: Session(db_module.engine))
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._started = False
        self._last_tick_at: datetime | None = None
        self._last_error: str | None = None

    @property
    def running(self) -> bool:
        return self._started and self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if not settings.scheduler_enabled:
            logger.info('scheduler disabled via settings')
            return
        if self._started:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, name='labos-scheduler', daemon=True)
        self._started = True
        self._thread.start()
        logger.info('scheduler started (tick=%ss)', settings.scheduler_tick_seconds)

    def stop(self) -> None:
        if not self._started:
            return
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        self._started = False
        self._thread = None
        logger.info('scheduler stopped')

    def _loop(self) -> None:
        tick_seconds = max(1.0, float(settings.scheduler_tick_seconds))
        while not self._stop_event.is_set():
            try:
                with self._session_factory() as session:
                    tick(session)
                self._last_tick_at = _utcnow()
                self._last_error = None
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception('scheduler loop error')
                self._last_error = str(exc)
            if self._stop_event.wait(tick_seconds):
                break

    def status(self) -> dict:
        return {
            'enabled': settings.scheduler_enabled,
            'running': self.running,
            'tick_seconds': settings.scheduler_tick_seconds,
            'last_tick_at': self._last_tick_at.isoformat() if self._last_tick_at else None,
            'last_error': self._last_error,
        }


_scheduler_runner = SchedulerRunner()


def get_scheduler_runner() -> SchedulerRunner:
    return _scheduler_runner
