"""ABrain Context Builder V1.

Baut einen strukturierten, deterministischen LabOS-Kontext zusammen, den
ABrain (extern) oder der lokale Fallback konsumiert. Nutzt ausschliesslich
bestehende LabOS-Services und -Daten. Kein ML, keine dynamische Entdeckung.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlmodel import Session, select

from ..config import settings
from ..models import (
    Alert,
    Asset,
    CalibrationRecord,
    Charge,
    DeviceNode,
    InventoryItem,
    MaintenanceRecord,
    Photo,
    Reactor,
    ReactorCommand,
    ReactorTwin,
    SafetyIncident,
    Schedule,
    ScheduleExecution,
    Task,
    TelemetryValue,
    VisionAnalysis,
    _utcnow,
)
from ..schemas import (
    ABrainAdapterContextRead,
    ABrainAdapterOperationsContext,
    ABrainAdapterReactorContext,
    ABrainAdapterResourceContext,
    ABrainAdapterResourceContextItem,
    ABrainAdapterScheduleContext,
    ABrainAdapterTelemetrySummary,
    ABrainAlertContextItemRead,
    ABrainContextSection,
    ABrainPhotoContextItemRead,
    ABrainSummaryCountsRead,
    ABrainTaskContextItemRead,
    AlertStatus,
    TaskStatus,
)
from . import reactor_health as reactor_health_service

_CONTRACT_VERSION = 'v1'
_DEFAULT_SECTIONS = [
    ABrainContextSection.tasks,
    ABrainContextSection.alerts,
    ABrainContextSection.sensors,
    ABrainContextSection.charges,
    ABrainContextSection.reactors,
    ABrainContextSection.photos,
]
_RECENT_FAILED_RUN_WINDOW = timedelta(hours=24)
_PARAMETER_RANGE_MAP = {
    'ph': ('target_ph_min', 'target_ph_max'),
    'temp': ('target_temp_min', 'target_temp_max'),
    'light': ('target_light_min', 'target_light_max'),
    'flow': ('target_flow_min', 'target_flow_max'),
}


def build_adapter_context(
    session: Session,
    *,
    include_sections: list[ABrainContextSection] | None = None,
    mode: str | None = None,
    fallback_used: bool = False,
) -> ABrainAdapterContextRead:
    now = _utcnow()
    sections = include_sections or list(_DEFAULT_SECTIONS)

    reactors = list(session.exec(select(Reactor).order_by(Reactor.name.asc(), Reactor.id.asc())).all())
    charges = list(session.exec(select(Charge)).all())
    tasks = list(session.exec(select(Task)).all())
    alerts = list(session.exec(select(Alert)).all())
    incidents = list(session.exec(select(SafetyIncident).where(SafetyIncident.status != 'resolved')).all())
    commands = list(session.exec(select(ReactorCommand)).all())
    calibration_due = _count_calibration_due(session)
    maintenance_overdue = _count_maintenance_overdue(session, now)
    reactor_ids = [reactor.id for reactor in reactors if reactor.id is not None]
    health_map = reactor_health_service.get_latest_for_reactors(session, reactor_ids)
    twin_map = _load_twin_map(session, reactor_ids)
    reactor_name_by_id = {reactor.id: reactor.name for reactor in reactors}
    charge_name_by_id = {charge.id: charge.name for charge in charges}

    open_tasks = [task for task in tasks if task.status != TaskStatus.done]
    overdue_tasks = [task for task in open_tasks if task.due_at is not None and task.due_at < now]
    due_today_tasks = [
        task for task in open_tasks if task.due_at is not None and task.due_at.date() == now.date()
    ]
    open_alerts = [alert for alert in alerts if alert.status != AlertStatus.resolved]
    critical_alerts = [alert for alert in open_alerts if alert.severity in {'high', 'critical'}]
    open_task_count_by_reactor = {
        reactor.id: sum(1 for task in open_tasks if task.reactor_id == reactor.id)
        for reactor in reactors
    }
    open_incident_count_by_reactor = {
        reactor.id: sum(1 for incident in incidents if incident.reactor_id == reactor.id)
        for reactor in reactors
    }
    recent_photos = _list_recent_photos(session)

    summary = ABrainSummaryCountsRead(
        open_tasks=len(open_tasks),
        overdue_tasks=len(overdue_tasks),
        due_today_tasks=len(due_today_tasks),
        critical_alerts=len(critical_alerts),
        open_alerts=len(open_alerts),
        sensor_attention=0,
        active_charges=sum(1 for charge in charges if charge.status == 'active'),
        reactors_online=sum(1 for reactor in reactors if reactor.status == 'online'),
        recent_photos=len(recent_photos),
    )

    reactor_contexts = [
        _build_reactor_context(
            session=session,
            reactor=reactor,
            twin=twin_map.get(reactor.id),
            health=health_map.get(reactor.id),
            open_task_count=open_task_count_by_reactor.get(reactor.id, 0),
            open_incident_count=open_incident_count_by_reactor.get(reactor.id, 0),
        )
        for reactor in reactors
    ]

    operations = ABrainAdapterOperationsContext(
        overdue_tasks=_serialize_tasks(overdue_tasks[:5], reactor_name_by_id, charge_name_by_id),
        critical_alerts=_serialize_alerts(critical_alerts[:5]),
        blocked_command_count=sum(1 for command in commands if command.status == 'blocked'),
        failed_command_count=sum(1 for command in commands if command.status in {'failed', 'timeout'}),
        due_calibration_count=calibration_due,
        overdue_maintenance_count=maintenance_overdue,
        open_safety_incident_count=len(incidents),
    )
    resources = _build_resource_context(session)
    schedule_context = _build_schedule_context(session, now)
    photos = _serialize_photos(recent_photos, reactor_name_by_id, charge_name_by_id)

    return ABrainAdapterContextRead(
        generated_at=now,
        contract_version=_CONTRACT_VERSION,
        mode=mode or settings.abrain_mode,
        fallback_used=fallback_used,
        summary=summary,
        reactors=reactor_contexts,
        operations=operations,
        resources=resources,
        schedule=schedule_context,
        photos=photos,
    )


def default_sections() -> list[ABrainContextSection]:
    return list(_DEFAULT_SECTIONS)


def contract_version() -> str:
    return _CONTRACT_VERSION


def _load_twin_map(session: Session, reactor_ids: list[int]) -> dict[int, ReactorTwin]:
    if not reactor_ids:
        return {}
    twins = list(session.exec(select(ReactorTwin).where(ReactorTwin.reactor_id.in_(reactor_ids))).all())
    return {twin.reactor_id: twin for twin in twins}


def _build_reactor_context(
    *,
    session: Session,
    reactor: Reactor,
    twin: ReactorTwin | None,
    health: Any,
    open_task_count: int,
    open_incident_count: int,
) -> ABrainAdapterReactorContext:
    telemetry_rows = _latest_telemetry(session, reactor.id)
    telemetry = [_build_telemetry_summary(row, twin) for row in telemetry_rows]
    latest_vision = _latest_vision(session, reactor.id)
    vision_label: str | None = None
    vision_confidence: float | None = None
    if latest_vision is not None:
        result = latest_vision.result or {}
        vision_label = result.get('health_label') if isinstance(result, dict) else None
        vision_confidence = latest_vision.confidence

    return ABrainAdapterReactorContext(
        id=reactor.id,
        name=reactor.name,
        status=reactor.status,
        phase=twin.current_phase if twin is not None else None,
        technical_state=twin.technical_state if twin is not None else None,
        biological_state=twin.biological_state if twin is not None else None,
        health_status=health.status if health is not None else None,
        health_summary=health.summary if health is not None else None,
        health_assessed_at=health.assessed_at if health is not None else None,
        open_task_count=open_task_count,
        open_incident_count=open_incident_count,
        telemetry=telemetry,
        latest_vision_label=vision_label,
        latest_vision_confidence=vision_confidence,
    )


def _latest_telemetry(session: Session, reactor_id: int) -> list[TelemetryValue]:
    rows = list(
        session.exec(
            select(TelemetryValue)
            .where(TelemetryValue.reactor_id == reactor_id)
            .order_by(TelemetryValue.timestamp.desc(), TelemetryValue.id.desc())
        ).all()
    )
    latest: dict[str, TelemetryValue] = {}
    for row in rows:
        latest.setdefault(row.sensor_type, row)
    return list(latest.values())


def _latest_vision(session: Session, reactor_id: int) -> VisionAnalysis | None:
    return session.exec(
        select(VisionAnalysis)
        .where(VisionAnalysis.reactor_id == reactor_id)
        .order_by(VisionAnalysis.created_at.desc(), VisionAnalysis.id.desc())
    ).first()


def _build_telemetry_summary(
    row: TelemetryValue,
    twin: ReactorTwin | None,
) -> ABrainAdapterTelemetrySummary:
    in_range: bool | None = None
    range_fields = _PARAMETER_RANGE_MAP.get(row.sensor_type)
    if twin is not None and range_fields is not None:
        low = getattr(twin, range_fields[0], None)
        high = getattr(twin, range_fields[1], None)
        if low is not None and row.value < low:
            in_range = False
        elif high is not None and row.value > high:
            in_range = False
        elif low is not None or high is not None:
            in_range = True
    return ABrainAdapterTelemetrySummary(
        sensor_type=row.sensor_type,
        latest_value=row.value,
        unit=row.unit,
        last_at=row.timestamp,
        in_range=in_range,
    )


def _serialize_tasks(
    tasks: list[Task],
    reactor_name_by_id: dict[int, str],
    charge_name_by_id: dict[int, str],
) -> list[ABrainTaskContextItemRead]:
    return [
        ABrainTaskContextItemRead(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            charge_name=charge_name_by_id.get(task.charge_id) if task.charge_id is not None else None,
            reactor_name=reactor_name_by_id.get(task.reactor_id) if task.reactor_id is not None else None,
        )
        for task in tasks
    ]


def _serialize_alerts(alerts: list[Alert]) -> list[ABrainAlertContextItemRead]:
    return [
        ABrainAlertContextItemRead(
            id=alert.id,
            title=alert.title,
            severity=alert.severity,
            status=alert.status,
            source_type=alert.source_type,
            created_at=alert.created_at,
        )
        for alert in alerts
    ]


def _serialize_photos(
    photos: list[Photo],
    reactor_name_by_id: dict[int, str],
    charge_name_by_id: dict[int, str],
) -> list[ABrainPhotoContextItemRead]:
    return [
        ABrainPhotoContextItemRead(
            id=photo.id,
            title=photo.title,
            created_at=photo.created_at,
            captured_at=photo.captured_at,
            charge_name=charge_name_by_id.get(photo.charge_id) if photo.charge_id is not None else None,
            reactor_name=reactor_name_by_id.get(photo.reactor_id) if photo.reactor_id is not None else None,
        )
        for photo in photos
    ]


def _list_recent_photos(session: Session, limit: int = 5) -> list[Photo]:
    rows = list(
        session.exec(
            select(Photo).order_by(Photo.created_at.desc(), Photo.id.desc())
        ).all()
    )
    return rows[:limit]


def _count_calibration_due(session: Session) -> int:
    return len(
        session.exec(
            select(CalibrationRecord.id).where(CalibrationRecord.status.in_(['due', 'expired']))
        ).all()
    )


def _count_maintenance_overdue(session: Session, now: datetime) -> int:
    return len(
        session.exec(
            select(MaintenanceRecord.id).where(
                MaintenanceRecord.status != 'completed',
                MaintenanceRecord.due_at.is_not(None),
                MaintenanceRecord.due_at < now,
            )
        ).all()
    )


def _build_resource_context(session: Session) -> ABrainAdapterResourceContext:
    inventory_items = list(session.exec(select(InventoryItem)).all())
    low_stock: list[ABrainAdapterResourceContextItem] = []
    out_of_stock: list[ABrainAdapterResourceContextItem] = []
    for item in inventory_items:
        quantity = item.quantity if isinstance(item.quantity, Decimal) else Decimal(str(item.quantity))
        if quantity <= Decimal('0'):
            out_of_stock.append(
                ABrainAdapterResourceContextItem(
                    kind='inventory',
                    id=item.id,
                    name=item.name,
                    detail=f'0 {item.unit} vorhanden',
                )
            )
            continue
        min_qty = item.min_quantity
        if min_qty is not None:
            min_decimal = min_qty if isinstance(min_qty, Decimal) else Decimal(str(min_qty))
            if quantity <= min_decimal:
                low_stock.append(
                    ABrainAdapterResourceContextItem(
                        kind='inventory',
                        id=item.id,
                        name=item.name,
                        detail=f'{quantity} {item.unit} (min {min_decimal})',
                    )
                )

    asset_rows = list(
        session.exec(
            select(Asset).where(Asset.status.in_(['maintenance', 'error', 'retired']))
        ).all()
    )
    assets_attention = [
        ABrainAdapterResourceContextItem(
            kind='asset',
            id=asset.id,
            name=asset.name,
            detail=f'Status {asset.status}',
        )
        for asset in asset_rows[:10]
    ]

    node_rows = list(
        session.exec(
            select(DeviceNode).where(DeviceNode.status.in_(['offline', 'error']))
        ).all()
    )
    offline_nodes = [
        ABrainAdapterResourceContextItem(
            kind='device_node',
            id=node.id,
            name=node.name,
            detail=f'Status {node.status}',
        )
        for node in node_rows[:10]
    ]
    return ABrainAdapterResourceContext(
        low_stock=low_stock[:10],
        out_of_stock=out_of_stock[:10],
        assets_attention=assets_attention,
        offline_nodes=offline_nodes,
    )


def _build_schedule_context(session: Session, now: datetime) -> ABrainAdapterScheduleContext:
    schedules = list(session.exec(select(Schedule)).all())
    active = [schedule for schedule in schedules if schedule.is_enabled]
    cutoff = now - _RECENT_FAILED_RUN_WINDOW
    recent_failures = list(
        session.exec(
            select(ScheduleExecution).where(
                ScheduleExecution.status.in_(['failed', 'error', 'blocked']),
                ScheduleExecution.started_at >= cutoff,
            )
        ).all()
    )
    schedule_items = [
        ABrainAdapterResourceContextItem(
            kind='schedule',
            id=schedule.id,
            name=schedule.name,
            detail=(
                f'{schedule.schedule_type} -> {schedule.target_type}'
                + (f' (last {schedule.last_status})' if schedule.last_status else '')
            ),
        )
        for schedule in active[:10]
    ]
    return ABrainAdapterScheduleContext(
        active_schedule_count=len(active),
        recent_failed_run_count=len(recent_failures),
        schedules=schedule_items,
    )
