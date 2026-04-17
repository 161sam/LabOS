from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Alert, Charge, Reactor, Task

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/summary')
def dashboard_summary(session: Session = Depends(get_session)):
    active_charges = len(session.exec(select(Charge).where(Charge.status == 'active')).all())
    reactors_online = len(session.exec(select(Reactor).where(Reactor.status == 'online')).all())
    open_alerts = len(session.exec(select(Alert).where(Alert.status == 'open')).all())
    today_tasks = len(session.exec(select(Task).where(Task.status == 'open')).all())
    return {
        'active_charges': active_charges,
        'reactors_online': reactors_online,
        'open_alerts': open_alerts,
        'today_tasks': today_tasks,
        'message': 'LabOS API erreichbar'
    }
