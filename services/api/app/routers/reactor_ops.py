from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    ReactorTwinCreate,
    ReactorTwinDetailRead,
    ReactorTwinPhaseUpdate,
    ReactorTwinRead,
    ReactorTwinStateUpdate,
    ReactorTwinUpdate,
)
from ..services import reactor_ops as reactor_ops_service

router = APIRouter(
    prefix='/reactor-ops',
    tags=['reactor-ops'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[ReactorTwinRead])
def list_reactor_ops(session: Session = Depends(get_session)):
    return reactor_ops_service.list_reactor_ops(session)


@router.get('/{reactor_id}', response_model=ReactorTwinDetailRead)
def get_reactor_ops(reactor_id: int, session: Session = Depends(get_session)):
    return reactor_ops_service.get_reactor_ops(session, reactor_id=reactor_id)


@router.post('', response_model=ReactorTwinRead, status_code=status.HTTP_201_CREATED)
def create_reactor_twin(
    payload: ReactorTwinCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_ops_service.create_reactor_twin(session, payload)


@router.put('/{reactor_id}', response_model=ReactorTwinRead)
def upsert_reactor_twin(
    reactor_id: int,
    payload: ReactorTwinUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_ops_service.upsert_reactor_twin(session, reactor_id=reactor_id, payload=payload)


@router.patch('/{reactor_id}/phase', response_model=ReactorTwinRead)
def update_reactor_twin_phase(
    reactor_id: int,
    payload: ReactorTwinPhaseUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_ops_service.update_reactor_twin_phase(session, reactor_id=reactor_id, payload=payload)


@router.patch('/{reactor_id}/state', response_model=ReactorTwinRead)
def update_reactor_twin_state(
    reactor_id: int,
    payload: ReactorTwinStateUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return reactor_ops_service.update_reactor_twin_state(session, reactor_id=reactor_id, payload=payload)
