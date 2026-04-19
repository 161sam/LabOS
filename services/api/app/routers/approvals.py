from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..auth import get_current_user, require_authenticated_user
from ..db import get_session
from ..schemas import (
    ApprovalDecisionPayload,
    ApprovalOverviewRead,
    ApprovalRequestRead,
    ApprovalRequestSource,
    ApprovalRequestStatus,
    UserRead,
)
from ..services import approvals as approvals_service

router = APIRouter(
    prefix='/approvals',
    tags=['approvals'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[ApprovalRequestRead])
def list_approvals(
    status: ApprovalRequestStatus | None = Query(default=None),
    action_name: str | None = Query(default=None),
    requested_by_source: ApprovalRequestSource | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return approvals_service.list_requests(
        session,
        status=status,
        action_name=action_name,
        requested_by_source=requested_by_source,
        trace_id=trace_id,
    )


@router.get('/overview', response_model=ApprovalOverviewRead)
def approvals_overview(session: Session = Depends(get_session)):
    return approvals_service.get_overview(session)


@router.get('/{request_id}', response_model=ApprovalRequestRead)
def get_approval(request_id: int, session: Session = Depends(get_session)):
    return approvals_service.get_request_read(session, request_id)


@router.post('/{request_id}/approve', response_model=ApprovalRequestRead)
def approve_approval(
    request_id: int,
    payload: ApprovalDecisionPayload,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return approvals_service.approve_request(session, request_id, current_user, payload)


@router.post('/{request_id}/reject', response_model=ApprovalRequestRead)
def reject_approval(
    request_id: int,
    payload: ApprovalDecisionPayload,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return approvals_service.reject_request(session, request_id, current_user, payload)
