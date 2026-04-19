from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import (
    IncidentStatus,
    SafetyIncidentCreate,
    SafetyIncidentRead,
    SafetyIncidentUpdate,
    SafetyOverviewRead,
)
from ..services import safety as safety_service

router = APIRouter(
    prefix='/safety',
    tags=['safety'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('/incidents', response_model=list[SafetyIncidentRead])
def list_safety_incidents(
    reactor_id: int | None = Query(default=None, ge=1),
    device_node_id: int | None = Query(default=None, ge=1),
    inc_status: IncidentStatus | None = Query(default=None, alias='status'),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return safety_service.list_safety_incidents(
        session,
        reactor_id=reactor_id,
        device_node_id=device_node_id,
        inc_status=inc_status,
        limit=limit,
    )


@router.post('/incidents', response_model=SafetyIncidentRead, status_code=status.HTTP_201_CREATED)
def create_safety_incident(
    payload: SafetyIncidentCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return safety_service.create_safety_incident(
        session, payload, created_by_user_id=current_user.id
    )


@router.patch('/incidents/{incident_id}', response_model=SafetyIncidentRead)
def update_safety_incident(
    incident_id: int,
    payload: SafetyIncidentUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_operator_user),
):
    return safety_service.update_safety_incident(session, incident_id, payload)


@router.get('/overview', response_model=SafetyOverviewRead)
def get_safety_overview(session: Session = Depends(get_session)):
    return safety_service.get_safety_overview(session)
