from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import ReactorCreate, ReactorEventCreate, ReactorEventRead, ReactorRead, ReactorStatusUpdate, ReactorUpdate, UserRead
from ..services import reactor_ops as reactor_ops_service
from ..services import reactors as reactor_service

router = APIRouter(prefix='/reactors', tags=['reactors'], dependencies=[Depends(require_authenticated_user)])


@router.get('', response_model=list[ReactorRead])
def list_reactors(session: Session = Depends(get_session)):
    return reactor_service.list_reactors(session)


@router.get('/{reactor_id}', response_model=ReactorRead)
def get_reactor(reactor_id: int, session: Session = Depends(get_session)):
    return reactor_service.get_reactor_or_404(session, reactor_id)


@router.post('', response_model=ReactorRead, status_code=status.HTTP_201_CREATED)
def create_reactor(
    payload: ReactorCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_service.create_reactor(session, payload)


@router.put('/{reactor_id}', response_model=ReactorRead)
def update_reactor(
    reactor_id: int,
    payload: ReactorUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    reactor = reactor_service.get_reactor_or_404(session, reactor_id)
    return reactor_service.update_reactor(session, reactor, payload)


@router.patch('/{reactor_id}/status', response_model=ReactorRead)
def update_reactor_status(
    reactor_id: int,
    payload: ReactorStatusUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    reactor = reactor_service.get_reactor_or_404(session, reactor_id)
    return reactor_service.update_reactor_status(session, reactor, payload)


@router.get('/{reactor_id}/events', response_model=list[ReactorEventRead])
def list_reactor_events(
    reactor_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    return reactor_ops_service.list_reactor_events(session, reactor_id=reactor_id, limit=limit)


@router.post('/{reactor_id}/events', response_model=ReactorEventRead, status_code=status.HTTP_201_CREATED)
def create_reactor_event(
    reactor_id: int,
    payload: ReactorEventCreate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(require_operator_user),
):
    return reactor_ops_service.create_reactor_event(
        session,
        reactor_id=reactor_id,
        payload=payload,
        created_by_user_id=current_user.id,
    )
