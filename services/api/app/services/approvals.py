"""Approval System V1 — queue, state, audit.

Approval Requests are LabOS domain/state objects. They do NOT implement
governance or planning logic: they are the operational queue that
captures approval-gated ABrain actions, tracks operator decisions, and
dispatches approved actions back through the existing static execution
layer (`abrain_execution`). Safety, role and domain guards remain
authoritative and are re-evaluated at execution time — approval is a
release, not a bypass.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import ApprovalRequest, UserAccount, _utcnow
from ..schemas import (
    ABrainActionDescriptor,
    ABrainActionRiskLevel,
    ABrainExecuteRequest,
    ABrainExecutionResult,
    ABrainExecutionStatus,
    ApprovalDecisionPayload,
    ApprovalOverviewRead,
    ApprovalRequestRead,
    ApprovalRequestSource,
    ApprovalRequestStatus,
    ApprovalRequestVia,
    UserRead,
    UserRole,
)


_HIGH_RISK_LEVELS = {ABrainActionRiskLevel.high, ABrainActionRiskLevel.critical}
_TERMINAL_STATUSES = {
    ApprovalRequestStatus.approved,
    ApprovalRequestStatus.rejected,
    ApprovalRequestStatus.executed,
    ApprovalRequestStatus.failed,
    ApprovalRequestStatus.cancelled,
}


def create_for_pending(
    session: Session,
    *,
    action_name: str,
    params: dict[str, Any],
    descriptor: ABrainActionDescriptor,
    user: UserRead,
    trace_id: str | None,
    source: str | None,
    reason: str | None,
    requested_via: str | None,
) -> ApprovalRequest:
    request = ApprovalRequest(
        action_name=action_name,
        action_params=params,
        requested_by_source=_coerce_source(source),
        requested_by_user_id=user.id,
        requested_via=_coerce_via(requested_via),
        trace_id=trace_id,
        risk_level=descriptor.risk_level.value if descriptor else None,
        status=ApprovalRequestStatus.pending.value,
        reason=reason,
        approval_required=True,
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return request


def list_requests(
    session: Session,
    *,
    status: ApprovalRequestStatus | None = None,
    action_name: str | None = None,
    requested_by_source: ApprovalRequestSource | None = None,
    trace_id: str | None = None,
) -> list[ApprovalRequestRead]:
    statement = select(ApprovalRequest)
    if status is not None:
        statement = statement.where(ApprovalRequest.status == status.value)
    if action_name is not None:
        statement = statement.where(ApprovalRequest.action_name == action_name)
    if requested_by_source is not None:
        statement = statement.where(ApprovalRequest.requested_by_source == requested_by_source.value)
    if trace_id is not None:
        statement = statement.where(ApprovalRequest.trace_id == trace_id)
    statement = statement.order_by(ApprovalRequest.created_at.desc(), ApprovalRequest.id.desc())
    requests = list(session.exec(statement).all())
    return [_serialize(session, request) for request in requests]


def get_request_or_404(session: Session, request_id: int) -> ApprovalRequest:
    request = session.get(ApprovalRequest, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Approval request not found')
    return request


def get_request_read(session: Session, request_id: int) -> ApprovalRequestRead:
    return _serialize(session, get_request_or_404(session, request_id))


def approve_request(
    session: Session,
    request_id: int,
    user: UserRead,
    payload: ApprovalDecisionPayload,
) -> ApprovalRequestRead:
    from . import abrain_execution  # local import to avoid import cycle

    request = get_request_or_404(session, request_id)
    _ensure_pending(request)
    _ensure_decision_role(user, request)

    execute_payload = ABrainExecuteRequest(
        action=request.action_name,
        params=dict(request.action_params or {}),
        trace_id=request.trace_id,
        source=f'approval:{user.username}',
        reason=request.reason,
        requested_via=request.requested_via,
        approve=True,
    )
    result: ABrainExecutionResult = abrain_execution.execute_action(session, execute_payload, user)

    request.approved_by_user_id = user.id
    request.decided_at = _utcnow()
    request.decision_note = payload.decision_note
    request.updated_at = _utcnow()
    request.executed_execution_log_id = result.log_id
    if result.status == ABrainExecutionStatus.executed:
        request.status = ApprovalRequestStatus.executed.value
        request.blocked_reason = None
        request.last_error = None
    elif result.status == ABrainExecutionStatus.blocked:
        request.status = ApprovalRequestStatus.failed.value
        request.blocked_reason = result.blocked_reason
        request.last_error = None
    elif result.status == ABrainExecutionStatus.rejected:
        # role/catalog rejection at execution boundary
        request.status = ApprovalRequestStatus.failed.value
        request.last_error = result.blocked_reason
    elif result.status == ABrainExecutionStatus.pending_approval:
        # should not happen because we pass approve=True, but stay defensive
        request.status = ApprovalRequestStatus.failed.value
        request.last_error = 'execution_returned_pending_approval'
    else:
        request.status = ApprovalRequestStatus.failed.value
        request.last_error = result.blocked_reason

    session.add(request)
    session.commit()
    session.refresh(request)
    return _serialize(session, request)


def reject_request(
    session: Session,
    request_id: int,
    user: UserRead,
    payload: ApprovalDecisionPayload,
) -> ApprovalRequestRead:
    request = get_request_or_404(session, request_id)
    _ensure_pending(request)
    _ensure_decision_role(user, request)

    request.status = ApprovalRequestStatus.rejected.value
    request.approved_by_user_id = user.id
    request.decided_at = _utcnow()
    request.decision_note = payload.decision_note
    request.updated_at = _utcnow()

    session.add(request)
    session.commit()
    session.refresh(request)
    return _serialize(session, request)


def get_overview(session: Session) -> ApprovalOverviewRead:
    counts = {status.value: 0 for status in ApprovalRequestStatus}
    high_risk_pending = 0
    for request in session.exec(select(ApprovalRequest)).all():
        counts[request.status] = counts.get(request.status, 0) + 1
        if request.status == ApprovalRequestStatus.pending.value and request.risk_level in {'high', 'critical'}:
            high_risk_pending += 1
    return ApprovalOverviewRead(
        pending=counts.get('pending', 0),
        approved=counts.get('approved', 0),
        rejected=counts.get('rejected', 0),
        executed=counts.get('executed', 0),
        failed=counts.get('failed', 0),
        cancelled=counts.get('cancelled', 0),
        high_risk_pending=high_risk_pending,
    )


def _ensure_pending(request: ApprovalRequest) -> None:
    if request.status != ApprovalRequestStatus.pending.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Approval request is already {request.status}',
        )


def _ensure_decision_role(user: UserRead, request: ApprovalRequest) -> None:
    if user.role == UserRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Operator or admin role required to decide approvals',
        )
    if request.risk_level in {'high', 'critical'} and user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin role required for high-risk approvals',
        )


def _serialize(session: Session, request: ApprovalRequest) -> ApprovalRequestRead:
    requested_by_username = _lookup_username(session, request.requested_by_user_id)
    approved_by_username = _lookup_username(session, request.approved_by_user_id)
    return ApprovalRequestRead(
        id=request.id,
        action_name=request.action_name,
        action_params=request.action_params or {},
        requested_by_source=ApprovalRequestSource(request.requested_by_source),
        requested_by_user_id=request.requested_by_user_id,
        requested_by_username=requested_by_username,
        requested_via=ApprovalRequestVia(request.requested_via),
        trace_id=request.trace_id,
        risk_level=ABrainActionRiskLevel(request.risk_level) if request.risk_level else None,
        status=ApprovalRequestStatus(request.status),
        reason=request.reason,
        decision_note=request.decision_note,
        approval_required=request.approval_required,
        approved_by_user_id=request.approved_by_user_id,
        approved_by_username=approved_by_username,
        decided_at=request.decided_at,
        executed_execution_log_id=request.executed_execution_log_id,
        blocked_reason=request.blocked_reason,
        last_error=request.last_error,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )


def _lookup_username(session: Session, user_id: int | None) -> str | None:
    if user_id is None:
        return None
    user = session.get(UserAccount, user_id)
    return user.username if user is not None else None


def _coerce_source(raw: str | None) -> str:
    if raw is None:
        return ApprovalRequestSource.abrain.value
    lowered = raw.lower()
    try:
        return ApprovalRequestSource(lowered).value
    except ValueError:
        if lowered.startswith('approval:') or lowered.startswith('operator'):
            return ApprovalRequestSource.operator.value
        return ApprovalRequestSource.abrain.value


def _coerce_via(raw: str | None) -> str:
    if raw is None:
        return ApprovalRequestVia.adapter.value
    try:
        return ApprovalRequestVia(raw).value
    except ValueError:
        return ApprovalRequestVia.adapter.value


__all__ = [
    'approve_request',
    'create_for_pending',
    'get_overview',
    'get_request_or_404',
    'get_request_read',
    'list_requests',
    'reject_request',
]
