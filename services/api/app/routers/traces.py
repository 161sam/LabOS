from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..auth import require_authenticated_user
from ..db import get_session
from ..schemas import (
    TraceContextDetailRead,
    TraceContextRead,
    TraceContextSource,
    TraceContextStatus,
)
from ..services import traces as traces_service

router = APIRouter(
    prefix='/traces',
    tags=['traces'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[TraceContextRead])
def list_traces(
    status: TraceContextStatus | None = Query(default=None),
    source: TraceContextSource | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return traces_service.list_traces(
        session,
        status_filter=status,
        source_filter=source,
        limit=limit,
    )


@router.get('/{trace_id}', response_model=TraceContextDetailRead)
def get_trace(trace_id: str, session: Session = Depends(get_session)):
    return traces_service.get_trace_detail(session, trace_id)
