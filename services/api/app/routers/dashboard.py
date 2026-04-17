from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Alert, Charge, Photo, Reactor, Sensor, Task
from ..schemas import DashboardSummaryRead
from ..services import alerts as alert_service
from ..services import photos as photo_service
from ..services import rules as rule_service
from ..services import sensors as sensor_service

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/summary', response_model=DashboardSummaryRead)
def dashboard_summary(session: Session = Depends(get_session)):
    today_start = datetime.combine(date.today(), time.min)
    tomorrow_start = today_start + timedelta(days=1)
    active_charges = len(session.exec(select(Charge).where(Charge.status == 'active')).all())
    reactors_online = len(session.exec(select(Reactor).where(Reactor.status == 'online')).all())
    active_sensors = len(session.exec(select(Sensor).where(Sensor.status == 'active')).all())
    error_sensors = len(session.exec(select(Sensor).where(Sensor.status == 'error')).all())
    open_tasks = len(session.exec(select(Task).where(Task.status != 'done')).all())
    due_today_tasks = len(
        session.exec(
            select(Task).where(
                Task.status != 'done',
                Task.due_at.is_not(None),
                Task.due_at >= today_start,
                Task.due_at < tomorrow_start,
            )
        ).all()
    )
    critical_alerts = len(
        session.exec(
            select(Alert).where(
                Alert.status != 'resolved',
                Alert.severity.in_(['high', 'critical']),
            )
        ).all()
    )
    open_alerts = len(session.exec(select(Alert).where(Alert.status != 'resolved')).all())
    photo_count = len(session.exec(select(Photo.id)).all())
    return {
        'active_charges': active_charges,
        'reactors_online': reactors_online,
        'active_sensors': active_sensors,
        'error_sensors': error_sensors,
        'open_tasks': open_tasks,
        'due_today_tasks': due_today_tasks,
        'critical_alerts': critical_alerts,
        'open_alerts': open_alerts,
        'photo_count': photo_count,
        'uploads_last_7_days': photo_service.count_recent_uploads(session, days=7),
        'active_rules': rule_service.count_active_rules(session),
        'sensor_overview': sensor_service.list_sensor_overview(session, limit=4),
        'recent_alerts': alert_service.list_alerts(session, limit=4),
        'recent_photos': photo_service.list_photos(session, latest=True, limit=4),
        'recent_rule_executions': rule_service.list_recent_executions(session, limit=4),
        'message': 'LabOS API erreichbar'
    }
