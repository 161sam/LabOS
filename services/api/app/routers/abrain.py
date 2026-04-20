from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..auth import get_current_user, require_admin_user, require_authenticated_user
from ..db import get_session
from ..schemas import (
    ABrainActionCatalogRead,
    ABrainAdapterContextRead,
    ABrainAdapterQueryRequest,
    ABrainAdapterResponse,
    ABrainContextRead,
    ABrainContextSection,
    ABrainExecuteRequest,
    ABrainExecutionLogRead,
    ABrainExecutionResult,
    ABrainExecutionStatus,
    ABrainPresetRead,
    ABrainQueryRequest,
    ABrainQueryResponse,
    ABrainReasoningRequest,
    ABrainReasoningResponse,
    ABrainStatusRead,
    UserRead,
)
from ..services import abrain as abrain_service
from ..services import abrain_actions, abrain_adapter, abrain_execution

router = APIRouter(
    prefix='/abrain',
    tags=['abrain'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('/status', response_model=ABrainStatusRead)
def abrain_status():
    return abrain_service.get_status()


@router.get('/presets', response_model=list[ABrainPresetRead])
def abrain_presets():
    return abrain_service.list_presets()


@router.get('/context', response_model=ABrainContextRead)
def abrain_context(
    include_sections: list[ABrainContextSection] | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return abrain_service.build_lab_context(session, include_sections=include_sections)


@router.post(
    '/query',
    response_model=ABrainQueryResponse,
    dependencies=[Depends(require_admin_user)],
)
def abrain_query(payload: ABrainQueryRequest, session: Session = Depends(get_session)):
    return abrain_service.query(session, payload)


@router.get('/actions', response_model=ABrainActionCatalogRead)
def abrain_actions_catalog():
    return abrain_actions.get_catalog()


@router.get('/adapter/context', response_model=ABrainAdapterContextRead)
def abrain_adapter_context(
    include_sections: list[ABrainContextSection] | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return abrain_adapter.build_context(session, include_sections=include_sections)


@router.post(
    '/adapter/query',
    response_model=ABrainAdapterResponse,
    dependencies=[Depends(require_admin_user)],
)
def abrain_adapter_query(
    payload: ABrainAdapterQueryRequest,
    session: Session = Depends(get_session),
):
    return abrain_adapter.query_adapter(session, payload)


@router.post(
    '/adapter/reason',
    response_model=ABrainReasoningResponse,
    dependencies=[Depends(require_admin_user)],
)
def abrain_adapter_reason(
    payload: ABrainReasoningRequest,
    session: Session = Depends(get_session),
):
    return abrain_adapter.query_reasoning(session, payload)


@router.post('/execute', response_model=ABrainExecutionResult)
def abrain_execute(
    payload: ABrainExecuteRequest,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return abrain_execution.execute_action(session, payload, current_user)


@router.get('/executions', response_model=list[ABrainExecutionLogRead])
def abrain_list_executions(
    status: ABrainExecutionStatus | None = Query(default=None),
    action: str | None = Query(default=None),
    trace_id: str | None = Query(default=None),
    executed_by: str | None = Query(default=None),
    approval_request_id: int | None = Query(default=None),
    has_approval: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return abrain_execution.list_execution_logs(
        session,
        status=status,
        action=action,
        trace_id=trace_id,
        executed_by=executed_by,
        approval_request_id=approval_request_id,
        has_approval=has_approval,
        limit=limit,
    )


@router.get('/executions/{log_id}', response_model=ABrainExecutionLogRead)
def abrain_get_execution(log_id: int, session: Session = Depends(get_session)):
    return abrain_execution.get_execution_log(session, log_id)
