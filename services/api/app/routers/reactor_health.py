from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..models import Reactor
from ..schemas import ReactorHealthAssessmentRead
from ..services import reactor_health as reactor_health_service

router = APIRouter(
    prefix='/reactor-health',
    tags=['reactor-health'],
    dependencies=[Depends(require_authenticated_user)],
)


def _reactor_name_map(session: Session, reactor_ids: list[int]) -> dict[int, str]:
    if not reactor_ids:
        return {}
    return {
        row.id: row.name
        for row in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    }


@router.get('', response_model=list[ReactorHealthAssessmentRead])
def list_reactor_health(session: Session = Depends(get_session)):
    assessments = reactor_health_service.list_latest_per_reactor(session)
    name_map = _reactor_name_map(session, [a.reactor_id for a in assessments])
    return [
        reactor_health_service.to_read(assessment, reactor_name=name_map.get(assessment.reactor_id))
        for assessment in assessments
    ]


@router.get('/{reactor_id}', response_model=ReactorHealthAssessmentRead)
def get_reactor_health(reactor_id: int, session: Session = Depends(get_session)):
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    assessment = reactor_health_service.get_latest_for_reactor(session, reactor_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No health assessment for this reactor yet')
    return reactor_health_service.to_read(assessment, reactor_name=reactor.name)


@router.get('/{reactor_id}/history', response_model=list[ReactorHealthAssessmentRead])
def list_reactor_health_history(
    reactor_id: int,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    reactor = session.get(Reactor, reactor_id)
    if reactor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Reactor not found')
    assessments = reactor_health_service.list_history_for_reactor(session, reactor_id, limit=limit)
    return [
        reactor_health_service.to_read(assessment, reactor_name=reactor.name)
        for assessment in assessments
    ]


@router.post(
    '/{reactor_id}/assess',
    response_model=ReactorHealthAssessmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
def trigger_reactor_assessment(reactor_id: int, session: Session = Depends(get_session)):
    assessment = reactor_health_service.assess_reactor(session, reactor_id)
    reactor = session.get(Reactor, reactor_id)
    return reactor_health_service.to_read(assessment, reactor_name=reactor.name if reactor else None)
