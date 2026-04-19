"""ABrain Execution + Governance Boundary V1.

Phase 3 of the ABrain Adapter Alignment. This module is the **only**
entry point by which ABrain-recommended actions are translated into
concrete LabOS state changes. It intentionally does not implement any
reasoning: it validates, role-checks, guards, dispatches to the
existing service-layer functions, and logs the outcome.

Key invariants:
- Execution dispatch uses a static `ACTION_MAP` — no eval/reflection,
  no dynamic registry. Unknown or unmapped actions are rejected.
- Role enforcement is derived from the static action catalog
  (`abrain_actions`); LabOS is the single authority on who may run
  what.
- Safety is never re-implemented here. Reactor commands delegate to
  `reactor_control.create_reactor_command`, which itself calls
  `safety_service.check_command_guards`.
- Approval gate: an action descriptor with `requires_approval=True`
  is executed only when the caller passes `approve=True`. Otherwise
  the attempt is recorded as `pending_approval` without side effects.
- Every attempt — executed, blocked, rejected, pending, failed — is
  persisted to `ABrainExecutionLog` with the adapter `trace_id` so
  the governance flow remains auditable.
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi import HTTPException, status as http_status
from sqlmodel import Session, select

from ..models import ABrainExecutionLog, ApprovalRequest
from ..schemas import (
    ABrainActionDescriptor,
    ABrainExecuteRequest,
    ABrainExecutionLogRead,
    ABrainExecutionResult,
    ABrainExecutionStatus,
    AlertCreate,
    ReactorCommandCreate,
    SafetyIncidentUpdate,
    TaskCreate,
    UserRead,
    UserRole,
)
from . import (
    abrain_actions,
    alerts as alerts_service,
    reactor_control,
    safety as safety_service,
    tasks as tasks_service,
)


_SOURCE_DEFAULT = 'abrain_adapter'


def _execute_create_task(session: Session, params: dict[str, Any]) -> dict[str, Any]:
    payload = TaskCreate(**params)
    result = tasks_service.create_task(session, payload)
    return result.model_dump(mode='json')


def _execute_create_alert(session: Session, params: dict[str, Any]) -> dict[str, Any]:
    payload = AlertCreate(**params)
    result = alerts_service.create_alert(session, payload)
    return result.model_dump(mode='json')


def _execute_create_reactor_command(session: Session, params: dict[str, Any]) -> dict[str, Any]:
    params = dict(params)
    reactor_id = params.pop('reactor_id', None)
    if not isinstance(reactor_id, int):
        raise HTTPException(status_code=422, detail='reactor_id is required')
    payload = ReactorCommandCreate(**params)
    result = reactor_control.create_reactor_command(session, reactor_id, payload)
    return result.model_dump(mode='json')


def _execute_retry_reactor_command(session: Session, params: dict[str, Any]) -> dict[str, Any]:
    command_id = params.get('command_id')
    if not isinstance(command_id, int):
        raise HTTPException(status_code=422, detail='command_id is required')
    result = reactor_control.retry_reactor_command(session, command_id)
    return result.model_dump(mode='json')


def _execute_ack_safety_incident(session: Session, params: dict[str, Any]) -> dict[str, Any]:
    incident_id = params.get('incident_id')
    if not isinstance(incident_id, int):
        raise HTTPException(status_code=422, detail='incident_id is required')
    update = SafetyIncidentUpdate(status='acknowledged', description=params.get('note'))
    result = safety_service.update_safety_incident(session, incident_id, update)
    return result.model_dump(mode='json')


# Static action dispatch table. No entries may be added at runtime.
ACTION_MAP: dict[str, Callable[[Session, dict[str, Any]], dict[str, Any]]] = {
    'labos.create_task': _execute_create_task,
    'labos.create_alert': _execute_create_alert,
    'labos.create_reactor_command': _execute_create_reactor_command,
    'labos.retry_reactor_command': _execute_retry_reactor_command,
    'labos.ack_safety_incident': _execute_ack_safety_incident,
}


def execute_action(
    session: Session,
    payload: ABrainExecuteRequest,
    user: UserRead,
) -> ABrainExecutionResult:
    action_name = payload.action
    params = dict(payload.params or {})
    source = payload.source or _SOURCE_DEFAULT
    trace_id = payload.trace_id

    if trace_id:
        from . import traces as traces_service  # local import to avoid cycles
        traces_service.ensure_trace(
            session,
            trace_id=trace_id,
            source=source,
            root_query=None,
            summary=None,
        )

    descriptor = abrain_actions.find_action(action_name)
    if descriptor is None or action_name not in ACTION_MAP:
        return _record(
            session,
            action=action_name,
            params=params,
            status=ABrainExecutionStatus.rejected,
            blocked_reason='action_not_in_catalog',
            descriptor=None,
            user=user,
            trace_id=trace_id,
            source=source,
            result={},
        )

    if not _role_allowed(user.role, descriptor.allowed_roles):
        return _record(
            session,
            action=action_name,
            params=params,
            status=ABrainExecutionStatus.rejected,
            blocked_reason=f'role_not_allowed: {user.role.value}',
            descriptor=descriptor,
            user=user,
            trace_id=trace_id,
            source=source,
            result={},
        )

    if descriptor.requires_approval and not payload.approve:
        from . import approvals as approvals_service  # local import to avoid import cycle

        approval = approvals_service.create_for_pending(
            session,
            action_name=action_name,
            params=params,
            descriptor=descriptor,
            user=user,
            trace_id=trace_id,
            source=source,
            reason=payload.reason,
            requested_via=payload.requested_via,
        )
        return _record(
            session,
            action=action_name,
            params=params,
            status=ABrainExecutionStatus.pending_approval,
            blocked_reason='approval_required',
            descriptor=descriptor,
            user=user,
            trace_id=trace_id,
            source=source,
            result={'approval_request_id': approval.id},
            approval_request_id=approval.id,
        )

    handler = ACTION_MAP[action_name]
    try:
        result_payload = handler(session, params)
    except HTTPException as exc:
        return _record(
            session,
            action=action_name,
            params=params,
            status=ABrainExecutionStatus.failed,
            blocked_reason=f'http_{exc.status_code}: {exc.detail}',
            descriptor=descriptor,
            user=user,
            trace_id=trace_id,
            source=source,
            result={},
        )
    except Exception as exc:  # noqa: BLE001 — boundary; failure is logged, not swallowed upstream
        return _record(
            session,
            action=action_name,
            params=params,
            status=ABrainExecutionStatus.failed,
            blocked_reason=f'exception: {exc.__class__.__name__}',
            descriptor=descriptor,
            user=user,
            trace_id=trace_id,
            source=source,
            result={},
        )

    status_value = ABrainExecutionStatus.executed
    blocked_reason: str | None = None
    if isinstance(result_payload, dict) and result_payload.get('status') == 'blocked':
        status_value = ABrainExecutionStatus.blocked
        blocked_reason = f"safety_guard: {result_payload.get('blocked_reason') or 'blocked'}"

    return _record(
        session,
        action=action_name,
        params=params,
        status=status_value,
        blocked_reason=blocked_reason,
        descriptor=descriptor,
        user=user,
        trace_id=trace_id,
        source=source,
        result=result_payload,
    )


def _role_allowed(role: UserRole, allowed_roles: list[str]) -> bool:
    return role.value in set(allowed_roles or [])


def _record(
    session: Session,
    *,
    action: str,
    params: dict[str, Any],
    status: ABrainExecutionStatus,
    blocked_reason: str | None,
    descriptor: ABrainActionDescriptor | None,
    user: UserRead,
    trace_id: str | None,
    source: str,
    result: dict[str, Any],
    approval_request_id: int | None = None,
) -> ABrainExecutionResult:
    log = ABrainExecutionLog(
        action=action,
        params=params,
        status=status.value,
        blocked_reason=blocked_reason,
        source=source,
        executed_by=user.username,
        trace_id=trace_id,
        result=result if isinstance(result, dict) else {'value': result},
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    if trace_id:
        from . import traces as traces_service  # local import to avoid cycles
        from ..schemas import TraceContextStatus as _TraceStatus
        if status == ABrainExecutionStatus.executed:
            traces_service.mark_status(session, trace_id, _TraceStatus.completed)
        elif status == ABrainExecutionStatus.failed or status == ABrainExecutionStatus.blocked:
            traces_service.mark_status(session, trace_id, _TraceStatus.failed)
        # pending_approval / rejected stay 'open'
    return ABrainExecutionResult(
        action=action,
        status=status,
        blocked_reason=blocked_reason,
        requires_approval=descriptor.requires_approval if descriptor else False,
        risk_level=descriptor.risk_level if descriptor else None,
        trace_id=trace_id,
        executed_by=user.username,
        source=source,
        result=log.result,
        log_id=log.id,
        approval_request_id=approval_request_id,
        created_at=log.created_at,
    )


def get_log_read(
    log: ABrainExecutionLog,
    *,
    approval_request_id: int | None = None,
) -> ABrainExecutionLogRead:
    return ABrainExecutionLogRead(
        id=log.id,
        action=log.action,
        params=log.params,
        status=ABrainExecutionStatus(log.status),
        blocked_reason=log.blocked_reason,
        source=log.source,
        executed_by=log.executed_by,
        trace_id=log.trace_id,
        approval_request_id=approval_request_id,
        result=log.result,
        created_at=log.created_at,
    )


def list_execution_logs(
    session: Session,
    *,
    status: ABrainExecutionStatus | None = None,
    action: str | None = None,
    trace_id: str | None = None,
    executed_by: str | None = None,
    approval_request_id: int | None = None,
    has_approval: bool | None = None,
    limit: int = 100,
) -> list[ABrainExecutionLogRead]:
    limit = max(1, min(int(limit), 500))

    target_log_id: int | None = None
    if approval_request_id is not None:
        approval = session.get(ApprovalRequest, approval_request_id)
        if approval is None or approval.executed_execution_log_id is None:
            return []
        target_log_id = approval.executed_execution_log_id

    statement = select(ABrainExecutionLog)
    if status is not None:
        statement = statement.where(ABrainExecutionLog.status == status.value)
    if action:
        statement = statement.where(ABrainExecutionLog.action == action)
    if trace_id:
        statement = statement.where(ABrainExecutionLog.trace_id == trace_id)
    if executed_by:
        statement = statement.where(ABrainExecutionLog.executed_by == executed_by)
    if target_log_id is not None:
        statement = statement.where(ABrainExecutionLog.id == target_log_id)
    statement = statement.order_by(
        ABrainExecutionLog.created_at.desc(),
        ABrainExecutionLog.id.desc(),
    ).limit(limit)

    logs = list(session.exec(statement).all())
    if not logs:
        return []

    approval_map = _build_approval_map(session, [log.id for log in logs])

    if has_approval is True:
        logs = [log for log in logs if log.id in approval_map]
    elif has_approval is False:
        logs = [log for log in logs if log.id not in approval_map]

    return [get_log_read(log, approval_request_id=approval_map.get(log.id)) for log in logs]


def get_execution_log(session: Session, log_id: int) -> ABrainExecutionLogRead:
    log = session.get(ABrainExecutionLog, log_id)
    if log is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail='Execution log not found',
        )
    approval_map = _build_approval_map(session, [log.id])
    return get_log_read(log, approval_request_id=approval_map.get(log.id))


def _build_approval_map(session: Session, log_ids: list[int]) -> dict[int, int]:
    if not log_ids:
        return {}
    approvals = list(
        session.exec(
            select(ApprovalRequest).where(
                ApprovalRequest.executed_execution_log_id.in_(log_ids)
            )
        ).all()
    )
    mapping: dict[int, int] = {}
    for approval in approvals:
        if approval.executed_execution_log_id is not None:
            mapping[approval.executed_execution_log_id] = approval.id
    return mapping


__all__ = [
    'ACTION_MAP',
    'execute_action',
    'get_execution_log',
    'get_log_read',
    'list_execution_logs',
]
