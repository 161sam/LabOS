from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Column, Index, JSON, Numeric
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Charge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    species: str
    status: str = Field(default='planned', index=True)
    volume_l: float = 1.0
    reactor_id: Optional[int] = Field(default=None, index=True)
    start_date: date = Field(default_factory=date.today, index=True)
    notes: Optional[str] = None


class Reactor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    reactor_type: str
    status: str = Field(default='online', index=True)
    volume_l: float = 1.0
    location: Optional[str] = None
    last_cleaned_at: Optional[datetime] = None
    notes: Optional[str] = None


class ReactorTwin(SQLModel, table=True):
    __table_args__ = (
        Index('ix_reactortwin_current_phase', 'current_phase'),
        Index('ix_reactortwin_technical_state', 'technical_state'),
        Index('ix_reactortwin_biological_state', 'biological_state'),
        Index('ix_reactortwin_contamination_state', 'contamination_state'),
        Index('ix_reactortwin_expected_harvest_window_start', 'expected_harvest_window_start'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', unique=True, index=True)
    culture_type: Optional[str] = None
    strain: Optional[str] = None
    medium_recipe: Optional[str] = None
    inoculated_at: Optional[datetime] = None
    current_phase: str = Field(default='growth')
    target_ph_min: Optional[float] = None
    target_ph_max: Optional[float] = None
    target_temp_min: Optional[float] = None
    target_temp_max: Optional[float] = None
    target_light_min: Optional[float] = None
    target_light_max: Optional[float] = None
    target_flow_min: Optional[float] = None
    target_flow_max: Optional[float] = None
    expected_harvest_window_start: Optional[datetime] = None
    expected_harvest_window_end: Optional[datetime] = None
    contamination_state: Optional[str] = None
    technical_state: str = Field(default='nominal')
    biological_state: str = Field(default='unknown')
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class ReactorEvent(SQLModel, table=True):
    __table_args__ = (
        Index('ix_reactorevent_reactor_id_created_at', 'reactor_id', 'created_at'),
        Index('ix_reactorevent_event_type', 'event_type'),
        Index('ix_reactorevent_severity', 'severity'),
        Index('ix_reactorevent_phase_snapshot', 'phase_snapshot'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', index=True)
    event_type: str
    title: str
    description: Optional[str] = None
    severity: Optional[str] = None
    phase_snapshot: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    created_by_user_id: Optional[int] = Field(default=None, foreign_key='useraccount.id', index=True)


class TelemetryValue(SQLModel, table=True):
    __table_args__ = (
        Index('ix_telemetryvalue_reactor_id_timestamp', 'reactor_id', 'timestamp'),
        Index('ix_telemetryvalue_sensor_type', 'sensor_type'),
        Index('ix_telemetryvalue_timestamp', 'timestamp'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', index=True)
    sensor_type: str
    value: float
    unit: str
    source: str = 'manual'
    timestamp: datetime = Field(default_factory=_utcnow)
    created_at: datetime = Field(default_factory=_utcnow)


class DeviceNode(SQLModel, table=True):
    __table_args__ = (
        Index('ix_devicenode_node_id', 'node_id', unique=True),
        Index('ix_devicenode_node_type', 'node_type'),
        Index('ix_devicenode_status', 'status'),
        Index('ix_devicenode_reactor_id', 'reactor_id'),
        Index('ix_devicenode_last_seen_at', 'last_seen_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    node_id: Optional[str] = Field(default=None, max_length=120)
    node_type: str
    status: str = 'online'
    last_seen_at: datetime = Field(default_factory=_utcnow)
    firmware_version: Optional[str] = None
    reactor_id: Optional[int] = Field(default=None, foreign_key='reactor.id', index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class ReactorSetpoint(SQLModel, table=True):
    __table_args__ = (
        Index('ix_reactorsetpoint_reactor_id_parameter', 'reactor_id', 'parameter'),
        Index('ix_reactorsetpoint_parameter', 'parameter'),
        Index('ix_reactorsetpoint_mode', 'mode'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', index=True)
    parameter: str
    target_value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mode: str = 'manual'
    updated_at: datetime = Field(default_factory=_utcnow)


def _new_command_uid() -> str:
    import uuid
    return uuid.uuid4().hex


class ReactorCommand(SQLModel, table=True):
    __table_args__ = (
        Index('ix_reactorcommand_reactor_id_created_at', 'reactor_id', 'created_at'),
        Index('ix_reactorcommand_status', 'status'),
        Index('ix_reactorcommand_command_type', 'command_type'),
        Index('ix_reactorcommand_command_uid', 'command_uid', unique=True),
        Index('ix_reactorcommand_timeout_at', 'timeout_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', index=True)
    command_type: str
    status: str = 'pending'
    blocked_reason: Optional[str] = None
    command_uid: str = Field(default_factory=_new_command_uid)
    published_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    timeout_at: Optional[datetime] = None
    ack_payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class CalibrationRecord(SQLModel, table=True):
    __table_args__ = (
        Index('ix_calibrationrecord_target_type_target_id', 'target_type', 'target_id'),
        Index('ix_calibrationrecord_status', 'status'),
        Index('ix_calibrationrecord_due_at', 'due_at'),
        Index('ix_calibrationrecord_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    target_type: str
    target_id: int
    parameter: str
    status: str = 'unknown'
    calibrated_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    calibration_value: Optional[float] = None
    reference_value: Optional[float] = None
    performed_by_user_id: Optional[int] = Field(default=None, foreign_key='useraccount.id')
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class MaintenanceRecord(SQLModel, table=True):
    __table_args__ = (
        Index('ix_maintenancerecord_target_type_target_id', 'target_type', 'target_id'),
        Index('ix_maintenancerecord_status', 'status'),
        Index('ix_maintenancerecord_due_at', 'due_at'),
        Index('ix_maintenancerecord_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    target_type: str
    target_id: int
    maintenance_type: str
    status: str = 'scheduled'
    performed_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    performed_by_user_id: Optional[int] = Field(default=None, foreign_key='useraccount.id')
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class SafetyIncident(SQLModel, table=True):
    __table_args__ = (
        Index('ix_safetyincident_reactor_id', 'reactor_id'),
        Index('ix_safetyincident_device_node_id', 'device_node_id'),
        Index('ix_safetyincident_status', 'status'),
        Index('ix_safetyincident_severity', 'severity'),
        Index('ix_safetyincident_incident_type', 'incident_type'),
        Index('ix_safetyincident_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: Optional[int] = Field(default=None, foreign_key='reactor.id')
    device_node_id: Optional[int] = Field(default=None, foreign_key='devicenode.id')
    asset_id: Optional[int] = None
    incident_type: str
    severity: str = 'warning'
    status: str = 'open'
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    resolved_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = Field(default=None, foreign_key='useraccount.id')


class Sensor(SQLModel, table=True):
    __table_args__ = (
        Index('ix_sensor_name', 'name'),
        Index('ix_sensor_status', 'status'),
        Index('ix_sensor_sensor_type', 'sensor_type'),
        Index('ix_sensor_reactor_id', 'reactor_id'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sensor_type: str
    unit: str
    reactor_id: Optional[int] = None
    status: str = 'active'
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class SensorValue(SQLModel, table=True):
    __table_args__ = (
        Index('ix_sensorvalue_recorded_at', 'recorded_at'),
        Index('ix_sensorvalue_sensor_id_recorded_at', 'sensor_id', 'recorded_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(index=True)
    value: float
    source: Optional[str] = None
    recorded_at: datetime = Field(default_factory=_utcnow)


class Task(SQLModel, table=True):
    __table_args__ = (
        Index('ix_task_status', 'status'),
        Index('ix_task_priority', 'priority'),
        Index('ix_task_due_at', 'due_at'),
        Index('ix_task_charge_id', 'charge_id'),
        Index('ix_task_reactor_id', 'reactor_id'),
        Index('ix_task_asset_id', 'asset_id'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = 'open'
    priority: str = 'normal'
    due_at: Optional[datetime] = None
    charge_id: Optional[int] = None
    reactor_id: Optional[int] = None
    asset_id: Optional[int] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    completed_at: Optional[datetime] = None


class Alert(SQLModel, table=True):
    __table_args__ = (
        Index('ix_alert_severity', 'severity'),
        Index('ix_alert_status', 'status'),
        Index('ix_alert_source_type', 'source_type'),
        Index('ix_alert_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    severity: str = 'info'
    status: str = 'open'
    source_type: str = 'system'
    source_id: Optional[int] = None
    created_at: datetime = Field(default_factory=_utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class Photo(SQLModel, table=True):
    __table_args__ = (
        Index('ix_photo_created_at', 'created_at'),
        Index('ix_photo_charge_id', 'charge_id'),
        Index('ix_photo_reactor_id', 'reactor_id'),
        Index('ix_photo_asset_id', 'asset_id'),
        Index('ix_photo_captured_at', 'captured_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    storage_path: str
    title: Optional[str] = None
    notes: Optional[str] = None
    charge_id: Optional[int] = None
    reactor_id: Optional[int] = None
    asset_id: Optional[int] = None
    created_at: datetime = Field(default_factory=_utcnow)
    uploaded_by: Optional[str] = None
    captured_at: Optional[datetime] = None


class Asset(SQLModel, table=True):
    __table_args__ = (
        Index('ix_asset_name', 'name'),
        Index('ix_asset_status', 'status'),
        Index('ix_asset_asset_type', 'asset_type'),
        Index('ix_asset_category', 'category'),
        Index('ix_asset_location', 'location'),
        Index('ix_asset_zone', 'zone'),
        Index('ix_asset_next_maintenance_at', 'next_maintenance_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    asset_type: str
    category: str
    status: str = 'active'
    location: str
    zone: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    notes: Optional[str] = None
    maintenance_notes: Optional[str] = None
    last_maintenance_at: Optional[datetime] = None
    next_maintenance_at: Optional[datetime] = None
    wiki_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class InventoryItem(SQLModel, table=True):
    __table_args__ = (
        Index('ix_inventoryitem_name', 'name'),
        Index('ix_inventoryitem_category', 'category'),
        Index('ix_inventoryitem_status', 'status'),
        Index('ix_inventoryitem_location', 'location'),
        Index('ix_inventoryitem_zone', 'zone'),
        Index('ix_inventoryitem_asset_id', 'asset_id'),
        Index('ix_inventoryitem_sku', 'sku'),
        Index('ix_inventoryitem_expiry_date', 'expiry_date'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    status: str = 'available'
    quantity: Decimal = Field(sa_column=Column(Numeric(12, 3), nullable=False, default=Decimal('0')))
    unit: str
    min_quantity: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 3), nullable=True))
    location: str
    zone: Optional[str] = None
    supplier: Optional[str] = None
    sku: Optional[str] = None
    notes: Optional[str] = None
    asset_id: Optional[int] = Field(default=None)
    wiki_ref: Optional[str] = None
    last_restocked_at: Optional[datetime] = None
    expiry_date: Optional[date] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class Label(SQLModel, table=True):
    __table_args__ = (
        Index('ix_label_label_type', 'label_type'),
        Index('ix_label_target_type', 'target_type'),
        Index('ix_label_target_type_target_id', 'target_type', 'target_id'),
        Index('ix_label_is_active', 'is_active'),
        Index('ix_label_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    label_code: str = Field(index=True, unique=True)
    label_type: str = 'qr'
    target_type: str
    target_id: int = Field(index=True)
    display_name: Optional[str] = None
    location_snapshot: Optional[str] = None
    note: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class UserAccount(SQLModel, table=True):
    __table_args__ = (
        Index('ix_useraccount_role', 'role'),
        Index('ix_useraccount_is_active', 'is_active'),
        Index('ix_useraccount_email', 'email'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    email: Optional[str] = None
    password_hash: str
    role: str = 'admin'
    is_active: bool = True
    auth_source: str = 'local'
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    last_login_at: Optional[datetime] = None


class Rule(SQLModel, table=True):
    __table_args__ = (
        Index('ix_rule_is_enabled', 'is_enabled'),
        Index('ix_rule_trigger_type', 'trigger_type'),
        Index('ix_rule_action_type', 'action_type'),
        Index('ix_rule_updated_at', 'updated_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    is_enabled: bool = True
    trigger_type: str
    condition_type: str
    condition_config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    action_type: str
    action_config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    last_evaluated_at: Optional[datetime] = None


class RuleExecution(SQLModel, table=True):
    __table_args__ = (
        Index('ix_ruleexecution_rule_id', 'rule_id'),
        Index('ix_ruleexecution_status', 'status'),
        Index('ix_ruleexecution_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: int = Field(index=True)
    status: str
    dry_run: bool = False
    evaluation_summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    action_result: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=_utcnow)


class Schedule(SQLModel, table=True):
    __table_args__ = (
        Index('ix_schedule_is_enabled', 'is_enabled'),
        Index('ix_schedule_schedule_type', 'schedule_type'),
        Index('ix_schedule_target_type', 'target_type'),
        Index('ix_schedule_next_run_at', 'next_run_at'),
        Index('ix_schedule_reactor_id', 'reactor_id'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    schedule_type: str
    interval_seconds: Optional[int] = None
    cron_expr: Optional[str] = None
    target_type: str
    target_id: Optional[int] = None
    reactor_id: Optional[int] = Field(default=None, foreign_key='reactor.id')
    target_params: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    is_enabled: bool = True
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    last_status: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class ScheduleExecution(SQLModel, table=True):
    __table_args__ = (
        Index('ix_scheduleexecution_schedule_id', 'schedule_id'),
        Index('ix_scheduleexecution_status', 'status'),
        Index('ix_scheduleexecution_started_at', 'started_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    schedule_id: int = Field(foreign_key='schedule.id', index=True)
    status: str
    trigger: str = 'scheduler'
    started_at: datetime = Field(default_factory=_utcnow)
    finished_at: Optional[datetime] = None
    result: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    error: Optional[str] = None


class VisionAnalysis(SQLModel, table=True):
    __table_args__ = (
        Index('ix_visionanalysis_photo_id', 'photo_id'),
        Index('ix_visionanalysis_reactor_id', 'reactor_id'),
        Index('ix_visionanalysis_analysis_type', 'analysis_type'),
        Index('ix_visionanalysis_status', 'status'),
        Index('ix_visionanalysis_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    photo_id: int = Field(foreign_key='photo.id')
    reactor_id: Optional[int] = Field(default=None, foreign_key='reactor.id')
    analysis_type: str = 'basic'
    status: str = 'ok'
    result: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    confidence: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class ReactorHealthAssessment(SQLModel, table=True):
    __table_args__ = (
        Index('ix_reactorhealthassessment_reactor_id', 'reactor_id'),
        Index('ix_reactorhealthassessment_status', 'status'),
        Index('ix_reactorhealthassessment_assessed_at', 'assessed_at'),
        Index('ix_reactorhealthassessment_created_at', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    reactor_id: int = Field(foreign_key='reactor.id', index=True)
    status: str = Field(default='unknown')
    summary: str = Field(default='')
    signals: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    source_telemetry_at: Optional[datetime] = None
    source_vision_analysis_id: Optional[int] = Field(default=None, foreign_key='visionanalysis.id')
    source_incident_count: int = 0
    assessed_at: datetime = Field(default_factory=_utcnow)
    created_at: datetime = Field(default_factory=_utcnow)


class WikiPage(SQLModel, table=True):
    slug: str = Field(primary_key=True)
    title: str
    summary: Optional[str] = None
