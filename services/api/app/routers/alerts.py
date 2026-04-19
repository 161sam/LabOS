from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..auth import require_authenticated_user, require_operator_user
from ..db import get_session
from ..schemas import AlertCreate, AlertRead, AlertSeverity, AlertStatus
from ..services import alerts as alert_service

router = APIRouter(
    prefix='/alerts',
    tags=['alerts'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('', response_model=list[AlertRead])
def list_alerts(
    status_filter: AlertStatus | None = Query(default=None, alias='status'),
    severity_filter: AlertSeverity | None = Query(default=None, alias='severity'),
    session: Session = Depends(get_session),
):
    return alert_service.list_alerts(session, status_filter=status_filter, severity_filter=severity_filter)


@router.get('/{alert_id}', response_model=AlertRead)
def get_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = alert_service.get_alert_or_404(session, alert_id)
    return AlertRead.model_validate(alert)


@router.post(
    '',
    response_model=AlertRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator_user)],
)
def create_alert(payload: AlertCreate, session: Session = Depends(get_session)):
    return alert_service.create_alert(session, payload)


@router.patch(
    '/{alert_id}/ack',
    response_model=AlertRead,
    dependencies=[Depends(require_operator_user)],
)
def acknowledge_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = alert_service.get_alert_or_404(session, alert_id)
    return alert_service.acknowledge_alert(session, alert)


@router.patch(
    '/{alert_id}/resolve',
    response_model=AlertRead,
    dependencies=[Depends(require_operator_user)],
)
def resolve_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = alert_service.get_alert_or_404(session, alert_id)
    return alert_service.resolve_alert(session, alert)
