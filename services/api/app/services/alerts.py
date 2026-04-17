from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import Alert, _utcnow
from ..schemas import AlertCreate, AlertRead, AlertSeverity, AlertStatus


def list_alerts(
    session: Session,
    status_filter: AlertStatus | None = None,
    severity_filter: AlertSeverity | None = None,
    limit: int | None = None,
) -> list[AlertRead]:
    statement = select(Alert)
    if status_filter is not None:
        statement = statement.where(Alert.status == status_filter.value)
    if severity_filter is not None:
        statement = statement.where(Alert.severity == severity_filter.value)

    alerts = list(session.exec(statement).all())
    alerts.sort(key=lambda alert: (alert.created_at, alert.id or 0), reverse=True)
    if limit is not None:
        alerts = alerts[:limit]
    return [AlertRead.model_validate(alert) for alert in alerts]


def get_alert_or_404(session: Session, alert_id: int) -> Alert:
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Alert not found')
    return alert


def create_alert(session: Session, payload: AlertCreate) -> AlertRead:
    alert = Alert(
        title=payload.title,
        message=payload.message,
        severity=payload.severity.value,
        status=payload.status.value,
        source_type=payload.source_type.value,
        source_id=payload.source_id,
    )
    if alert.status == AlertStatus.acknowledged.value:
        alert.acknowledged_at = _utcnow()
    if alert.status == AlertStatus.resolved.value:
        now = _utcnow()
        alert.acknowledged_at = now
        alert.resolved_at = now
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return AlertRead.model_validate(alert)


def acknowledge_alert(session: Session, alert: Alert) -> AlertRead:
    if alert.status == AlertStatus.resolved.value:
        return AlertRead.model_validate(alert)

    alert.status = AlertStatus.acknowledged.value
    alert.acknowledged_at = alert.acknowledged_at or _utcnow()
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return AlertRead.model_validate(alert)


def resolve_alert(session: Session, alert: Alert) -> AlertRead:
    now = _utcnow()
    alert.status = AlertStatus.resolved.value
    alert.acknowledged_at = alert.acknowledged_at or now
    alert.resolved_at = now
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return AlertRead.model_validate(alert)
