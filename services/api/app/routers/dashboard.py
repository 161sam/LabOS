from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..auth import require_authenticated_user
from ..db import get_session
from ..models import Alert, Asset, Charge, Photo, Reactor, Sensor, Task
from ..schemas import DashboardSummaryRead
from ..services import assets as asset_service
from ..services import alerts as alert_service
from ..services import calibration as calibration_service
from ..services import inventory as inventory_service
from ..services import labels as label_service
from ..services import maintenance as maintenance_service
from ..services import photos as photo_service
from ..services import reactor_control as reactor_control_service
from ..services import reactor_health as reactor_health_service
from ..services import reactor_ops as reactor_ops_service
from ..services import rules as rule_service
from ..services import modules as module_service
from ..services import infra as infra_service
from ..services import safety as safety_service
from ..services import sensors as sensor_service

router = APIRouter(
    prefix='/dashboard',
    tags=['dashboard'],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get('/summary', response_model=DashboardSummaryRead)
def dashboard_summary(session: Session = Depends(get_session)):
    today_start = datetime.combine(date.today(), time.min)
    tomorrow_start = today_start + timedelta(days=1)
    active_charges = len(session.exec(select(Charge).where(Charge.status == 'active')).all())
    reactors_online = len(session.exec(select(Reactor).where(Reactor.status == 'online')).all())
    reactors_attention = reactor_ops_service.count_reactors_with_attention(session)
    reactors_harvest_ready = reactor_ops_service.count_harvest_ready_reactors(session)
    reactors_incident_or_contamination = reactor_ops_service.count_reactors_with_incident_or_contamination(session)
    health_counts = reactor_health_service.count_by_status(session)
    offline_devices = reactor_control_service.count_offline_devices(session)
    active_sensors = len(session.exec(select(Sensor).where(Sensor.status == 'active')).all())
    error_sensors = len(session.exec(select(Sensor).where(Sensor.status == 'error')).all())
    active_assets = len(session.exec(select(Asset).where(Asset.status == 'active')).all())
    assets_in_maintenance = len(session.exec(select(Asset).where(Asset.status == 'maintenance')).all())
    assets_in_error = len(session.exec(select(Asset).where(Asset.status == 'error')).all())
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
    asset_overview = asset_service.get_asset_overview(session)
    module_overview = module_service.get_module_overview(session)
    infra_overview = infra_service.get_overview(session)
    inventory_overview = inventory_service.get_inventory_overview(session)
    label_overview = label_service.get_label_overview(session)
    return {
        'active_charges': active_charges,
        'reactors_online': reactors_online,
        'reactors_attention': reactors_attention,
        'reactors_harvest_ready': reactors_harvest_ready,
        'reactors_incident_or_contamination': reactors_incident_or_contamination,
        'reactors_health_nominal': health_counts.get('nominal', 0),
        'reactors_health_attention': health_counts.get('attention', 0),
        'reactors_health_warning': health_counts.get('warning', 0),
        'reactors_health_incident': health_counts.get('incident', 0),
        'reactors_health_unknown': health_counts.get('unknown', 0),
        'offline_devices': offline_devices,
        'active_sensors': active_sensors,
        'error_sensors': error_sensors,
        'active_assets': active_assets,
        'assets_in_maintenance': assets_in_maintenance,
        'assets_in_error': assets_in_error,
        'labeled_assets': label_overview.labeled_assets,
        'inventory_items': inventory_overview.total_items,
        'inventory_low_stock': inventory_overview.low_stock_items,
        'inventory_out_of_stock': inventory_overview.out_of_stock_items,
        'labeled_inventory_items': label_overview.labeled_inventory_items,
        'open_tasks': open_tasks,
        'due_today_tasks': due_today_tasks,
        'critical_alerts': critical_alerts,
        'open_alerts': open_alerts,
        'photo_count': photo_count,
        'uploads_last_7_days': photo_service.count_recent_uploads(session, days=7),
        'active_rules': rule_service.count_active_rules(session),
        'open_safety_incidents': safety_service.count_open_incidents(session),
        'calibration_due_or_expired': calibration_service.count_due_or_expired(session),
        'maintenance_overdue': maintenance_service.count_overdue(session),
        'sensor_overview': sensor_service.list_sensor_overview(session, limit=4),
        'reactor_telemetry_overview': reactor_control_service.list_reactor_telemetry_overview(session),
        'recent_alerts': alert_service.list_alerts(session, limit=4),
        'recent_photos': photo_service.list_photos(session, latest=True, limit=4),
        'recent_reactor_events': reactor_ops_service.list_recent_events(session, limit=4),
        'recent_rule_executions': rule_service.list_recent_executions(session, limit=4),
        'upcoming_maintenance_assets': asset_overview.upcoming_maintenance_assets,
        'critical_inventory_items': inventory_overview.critical_items,
        'recent_labels': label_overview.recent_labels,
        'recent_safety_incidents': safety_service.list_safety_incidents(session, limit=4),
        'autonomous_modules_total': module_overview.total_modules,
        'autonomous_modules_warning_or_incident': (
            module_overview.attention_modules
            + module_overview.warning_modules
            + module_overview.incident_modules
            + module_overview.offline_modules
        ),
        'infra_nodes_total': infra_overview.total_nodes,
        'infra_nodes_offline_or_incident': (
            infra_overview.offline_nodes + infra_overview.incident_nodes
        ),
        'infra_services_degraded': infra_overview.degraded_services,
        'infra_backup_failures_recent': infra_overview.recent_backup_failures,
        'message': 'LabOS API erreichbar'
    }
