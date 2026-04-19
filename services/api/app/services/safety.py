"""Safety — GUARD / CONSTRAINT layer (not a decision layer).

Boundary Hardening V1: safety is the ONLY place in LabOS authorized to
block a command. This is an invariant of the architecture, not a policy
decision. A guard answers the narrow question "is executing this
command right now a safety violation?"; it does NOT answer "should this
command exist in the first place?".

`blocked_reason` strings are prefixed with `safety_guard:` so the
intent is explicit at the API boundary. Every other decision
(planning, prioritization, orchestration) belongs to ABrain.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models import SafetyIncident, Reactor, DeviceNode, ReactorCommand, UserAccount, _utcnow
from ..schemas import (
    SafetyIncidentCreate,
    SafetyIncidentRead,
    SafetyIncidentUpdate,
    SafetyOverviewRead,
    IncidentStatus,
)
from . import calibration as calibration_service
from . import maintenance as maintenance_service


def list_safety_incidents(
    session: Session,
    *,
    reactor_id: int | None = None,
    device_node_id: int | None = None,
    inc_status: IncidentStatus | None = None,
    limit: int = 100,
) -> list[SafetyIncidentRead]:
    statement = select(SafetyIncident)
    if reactor_id is not None:
        statement = statement.where(SafetyIncident.reactor_id == reactor_id)
    if device_node_id is not None:
        statement = statement.where(SafetyIncident.device_node_id == device_node_id)
    if inc_status is not None:
        statement = statement.where(SafetyIncident.status == inc_status.value)
    statement = statement.order_by(SafetyIncident.created_at.desc(), SafetyIncident.id.desc()).limit(limit)
    incidents = list(session.exec(statement).all())
    return _serialize_incidents(session, incidents)


def create_safety_incident(
    session: Session,
    payload: SafetyIncidentCreate,
    *,
    created_by_user_id: int | None = None,
) -> SafetyIncidentRead:
    incident = SafetyIncident(
        reactor_id=payload.reactor_id,
        device_node_id=payload.device_node_id,
        asset_id=payload.asset_id,
        incident_type=payload.incident_type.value,
        severity=payload.severity.value,
        status='open',
        title=payload.title,
        description=payload.description,
        created_at=_utcnow(),
        created_by_user_id=created_by_user_id,
    )
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return _serialize_incidents(session, [incident])[0]


def update_safety_incident(
    session: Session,
    incident_id: int,
    payload: SafetyIncidentUpdate,
) -> SafetyIncidentRead:
    incident = get_incident_or_404(session, incident_id)
    if payload.status is not None:
        incident.status = payload.status.value
        if payload.status == IncidentStatus.resolved and incident.resolved_at is None:
            incident.resolved_at = _utcnow()
    if payload.severity is not None:
        incident.severity = payload.severity.value
    if 'description' in payload.model_fields_set:
        incident.description = payload.description
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return _serialize_incidents(session, [incident])[0]


def get_safety_overview(session: Session) -> SafetyOverviewRead:
    incidents = list(session.exec(select(SafetyIncident)).all())
    open_count = sum(1 for i in incidents if i.status == 'open')
    ack_count = sum(1 for i in incidents if i.status == 'acknowledged')
    critical_count = sum(1 for i in incidents if i.severity == 'critical' and i.status != 'resolved')
    high_count = sum(1 for i in incidents if i.severity == 'high' and i.status != 'resolved')
    blocked = len(
        session.exec(select(ReactorCommand.id).where(ReactorCommand.status == 'blocked')).all()
    )
    cal_expired = calibration_service.count_due_or_expired(session)
    maint_overdue = maintenance_service.count_overdue(session)
    return SafetyOverviewRead(
        open_incidents=open_count,
        acknowledged_incidents=ack_count,
        critical_incidents=critical_count,
        high_incidents=high_count,
        blocked_commands=blocked,
        calibration_expired=cal_expired,
        maintenance_overdue=maint_overdue,
    )


def count_open_incidents(session: Session) -> int:
    return len(
        session.exec(select(SafetyIncident.id).where(SafetyIncident.status == 'open')).all()
    )


def has_critical_open_incident_for_reactor(session: Session, reactor_id: int) -> SafetyIncident | None:
    return session.exec(
        select(SafetyIncident).where(
            SafetyIncident.reactor_id == reactor_id,
            SafetyIncident.severity == 'critical',
            SafetyIncident.status != 'resolved',
        )
    ).first()


def check_command_guards(
    session: Session,
    reactor_id: int,
    command_type: str,
) -> str | None:
    """Return a blocked_reason string if the command should be blocked, else None."""
    critical_incident = has_critical_open_incident_for_reactor(session, reactor_id)
    if critical_incident is not None:
        return (
            f'safety_guard: blocked — critical safety incident open '
            f'(#{critical_incident.id}: {critical_incident.title})'
        )

    reactor_nodes = list(
        session.exec(
            select(DeviceNode).where(DeviceNode.reactor_id == reactor_id)
        ).all()
    )
    offline_nodes = [n for n in reactor_nodes if n.status in ('offline', 'error')]
    if offline_nodes and command_type in ('pump_on', 'aeration_start', 'sample_capture'):
        node_names = ', '.join(n.name for n in offline_nodes[:3])
        return (
            f'safety_guard: blocked — reactor node(s) offline or in error state '
            f'({node_names})'
        )

    if command_type in ('pump_on', 'aeration_start'):
        dry_run = session.exec(
            select(SafetyIncident).where(
                SafetyIncident.reactor_id == reactor_id,
                SafetyIncident.incident_type == 'dry_run_risk',
                SafetyIncident.status != 'resolved',
            )
        ).first()
        if dry_run is not None:
            return f'safety_guard: blocked — dry_run_risk incident open (#{dry_run.id})'

    if command_type == 'sample_capture':
        expired_cal = calibration_service.has_expired_calibration_for_target(
            session, 'reactor', reactor_id
        )
        if expired_cal:
            return (
                'safety_guard: blocked — expired or failed calibration record '
                'exists for this reactor'
            )

    return None


def get_incident_or_404(session: Session, incident_id: int) -> SafetyIncident:
    incident = session.get(SafetyIncident, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Safety incident not found')
    return incident


def _serialize_incidents(session: Session, incidents: list[SafetyIncident]) -> list[SafetyIncidentRead]:
    if not incidents:
        return []
    reactor_ids = sorted({i.reactor_id for i in incidents if i.reactor_id is not None})
    reactor_map = {
        r.id: r.name
        for r in session.exec(select(Reactor).where(Reactor.id.in_(reactor_ids))).all()
    } if reactor_ids else {}
    node_ids = sorted({i.device_node_id for i in incidents if i.device_node_id is not None})
    node_map = {
        n.id: n.name
        for n in session.exec(select(DeviceNode).where(DeviceNode.id.in_(node_ids))).all()
    } if node_ids else {}
    user_ids = sorted({i.created_by_user_id for i in incidents if i.created_by_user_id is not None})
    user_map = {
        u.id: u.username
        for u in session.exec(select(UserAccount).where(UserAccount.id.in_(user_ids))).all()
    } if user_ids else {}
    return [
        SafetyIncidentRead(
            id=i.id,
            reactor_id=i.reactor_id,
            reactor_name=reactor_map.get(i.reactor_id) if i.reactor_id else None,
            device_node_id=i.device_node_id,
            device_node_name=node_map.get(i.device_node_id) if i.device_node_id else None,
            asset_id=i.asset_id,
            incident_type=i.incident_type,
            severity=i.severity,
            status=i.status,
            title=i.title,
            description=i.description,
            created_at=i.created_at,
            resolved_at=i.resolved_at,
            created_by_user_id=i.created_by_user_id,
            created_by_username=user_map.get(i.created_by_user_id) if i.created_by_user_id else None,
        )
        for i in incidents
    ]
