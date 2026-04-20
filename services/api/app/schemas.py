from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ChargeStatus(str, Enum):
    planned = 'planned'
    active = 'active'
    paused = 'paused'
    completed = 'completed'
    archived = 'archived'


class ReactorStatus(str, Enum):
    online = 'online'
    offline = 'offline'
    cleaning = 'cleaning'
    maintenance = 'maintenance'


class ReactorPhase(str, Enum):
    inoculation = 'inoculation'
    growth = 'growth'
    stabilization = 'stabilization'
    harvest_ready = 'harvest_ready'
    maintenance = 'maintenance'
    paused = 'paused'
    incident = 'incident'


class ReactorTechnicalState(str, Enum):
    nominal = 'nominal'
    warning = 'warning'
    maintenance = 'maintenance'
    degraded = 'degraded'
    error = 'error'


class ReactorBiologicalState(str, Enum):
    stable = 'stable'
    adapting = 'adapting'
    growing = 'growing'
    stressed = 'stressed'
    contaminated = 'contaminated'
    unknown = 'unknown'


class ReactorContaminationState(str, Enum):
    suspected = 'suspected'
    confirmed = 'confirmed'
    recovering = 'recovering'
    cleared = 'cleared'


class ReactorEventType(str, Enum):
    inoculation = 'inoculation'
    medium_change = 'medium_change'
    calibration = 'calibration'
    contamination_suspected = 'contamination_suspected'
    contamination_confirmed = 'contamination_confirmed'
    maintenance = 'maintenance'
    manual_adjustment = 'manual_adjustment'
    observation = 'observation'
    harvest = 'harvest'
    incident = 'incident'


class TelemetrySensorType(str, Enum):
    temp = 'temp'
    ph = 'ph'
    light = 'light'
    flow = 'flow'
    ec = 'ec'
    co2 = 'co2'
    humidity = 'humidity'


class TelemetrySource(str, Enum):
    manual = 'manual'
    device = 'device'
    simulated = 'simulated'


class DeviceNodeType(str, Enum):
    sampling = 'sampling'
    env_control = 'env_control'
    sensor_bridge = 'sensor_bridge'
    pump_driver = 'pump_driver'
    light_controller = 'light_controller'
    dosing = 'dosing'
    safety = 'safety'
    vision = 'vision'


class DeviceNodeStatus(str, Enum):
    online = 'online'
    offline = 'offline'
    warning = 'warning'
    error = 'error'


class ReactorControlParameter(str, Enum):
    temp = 'temp'
    ph = 'ph'
    light = 'light'
    flow = 'flow'
    ec = 'ec'
    co2 = 'co2'
    humidity = 'humidity'


class ReactorSetpointMode(str, Enum):
    auto = 'auto'
    manual = 'manual'


class ReactorCommandType(str, Enum):
    light_on = 'light_on'
    light_off = 'light_off'
    pump_on = 'pump_on'
    pump_off = 'pump_off'
    aeration_start = 'aeration_start'
    aeration_stop = 'aeration_stop'
    sample_capture = 'sample_capture'


class ReactorCommandStatus(str, Enum):
    pending = 'pending'
    sent = 'sent'
    acknowledged = 'acknowledged'
    failed = 'failed'
    blocked = 'blocked'
    timeout = 'timeout'
    retrying = 'retrying'


class MQTTAckStatus(str, Enum):
    ok = 'ok'
    error = 'error'


class CalibrationTargetType(str, Enum):
    reactor = 'reactor'
    device_node = 'device_node'
    asset = 'asset'


class CalibrationStatus(str, Enum):
    valid = 'valid'
    due = 'due'
    expired = 'expired'
    failed = 'failed'
    unknown = 'unknown'


class MaintenanceTargetType(str, Enum):
    reactor = 'reactor'
    device_node = 'device_node'
    asset = 'asset'


class MaintenanceType(str, Enum):
    cleaning = 'cleaning'
    inspection = 'inspection'
    replacement = 'replacement'
    tubing_flush = 'tubing_flush'
    filter_change = 'filter_change'
    pump_service = 'pump_service'
    general_service = 'general_service'


class MaintenanceStatus(str, Enum):
    scheduled = 'scheduled'
    done = 'done'
    overdue = 'overdue'
    skipped = 'skipped'


class IncidentType(str, Enum):
    sensor_untrusted = 'sensor_untrusted'
    calibration_expired = 'calibration_expired'
    node_offline = 'node_offline'
    overheating_risk = 'overheating_risk'
    dry_run_risk = 'dry_run_risk'
    clogging_suspected = 'clogging_suspected'
    flow_mismatch = 'flow_mismatch'
    invalid_telemetry = 'invalid_telemetry'
    unsafe_command_blocked = 'unsafe_command_blocked'
    general = 'general'


class IncidentSeverity(str, Enum):
    info = 'info'
    warning = 'warning'
    high = 'high'
    critical = 'critical'


class IncidentStatus(str, Enum):
    open = 'open'
    acknowledged = 'acknowledged'
    resolved = 'resolved'


class AssetType(str, Enum):
    printer_3d = 'printer_3d'
    microscope = 'microscope'
    soldering_station = 'soldering_station'
    power_supply = 'power_supply'
    pump = 'pump'
    server = 'server'
    gpu_node = 'gpu_node'
    sbc = 'sbc'
    network_device = 'network_device'
    lab_device = 'lab_device'
    tool = 'tool'


class AssetStatus(str, Enum):
    active = 'active'
    maintenance = 'maintenance'
    error = 'error'
    inactive = 'inactive'
    retired = 'retired'


class InventoryStatus(str, Enum):
    available = 'available'
    low_stock = 'low_stock'
    out_of_stock = 'out_of_stock'
    reserved = 'reserved'
    expired = 'expired'
    archived = 'archived'


class LabelType(str, Enum):
    qr = 'qr'
    printed_label = 'printed_label'


class LabelTargetType(str, Enum):
    asset = 'asset'
    inventory_item = 'inventory_item'


class UserRole(str, Enum):
    admin = 'admin'
    operator = 'operator'
    viewer = 'viewer'


class SensorType(str, Enum):
    temperature = 'temperature'
    humidity = 'humidity'
    water_temperature = 'water_temperature'
    ph = 'ph'
    ec = 'ec'
    light = 'light'
    co2 = 'co2'


class SensorStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'
    error = 'error'
    maintenance = 'maintenance'


class TaskStatus(str, Enum):
    open = 'open'
    doing = 'doing'
    blocked = 'blocked'
    done = 'done'


class TaskPriority(str, Enum):
    low = 'low'
    normal = 'normal'
    high = 'high'
    critical = 'critical'


class AlertSeverity(str, Enum):
    info = 'info'
    warning = 'warning'
    high = 'high'
    critical = 'critical'


class AlertStatus(str, Enum):
    open = 'open'
    acknowledged = 'acknowledged'
    resolved = 'resolved'


class AlertSourceType(str, Enum):
    system = 'system'
    sensor = 'sensor'
    charge = 'charge'
    reactor = 'reactor'
    manual = 'manual'


class ABrainPreset(str, Enum):
    daily_overview = 'daily_overview'
    critical_issues = 'critical_issues'
    overdue_tasks = 'overdue_tasks'
    sensor_attention = 'sensor_attention'
    reactor_attention = 'reactor_attention'
    recent_activity = 'recent_activity'


class ABrainContextSection(str, Enum):
    tasks = 'tasks'
    alerts = 'alerts'
    sensors = 'sensors'
    charges = 'charges'
    reactors = 'reactors'
    photos = 'photos'


class RuleTriggerType(str, Enum):
    sensor_threshold = 'sensor_threshold'
    stale_sensor = 'stale_sensor'
    overdue_tasks = 'overdue_tasks'
    reactor_status = 'reactor_status'


class RuleConditionType(str, Enum):
    threshold_gt = 'threshold_gt'
    threshold_lt = 'threshold_lt'
    age_gt_hours = 'age_gt_hours'
    count_gt = 'count_gt'
    status_is = 'status_is'


class RuleActionType(str, Enum):
    create_alert = 'create_alert'
    create_task = 'create_task'


class RuleExecutionStatus(str, Enum):
    matched = 'matched'
    not_matched = 'not_matched'
    executed = 'executed'
    failed = 'failed'


class AppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _normalize_required_text(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError('must not be empty')
    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class ChargePayload(AppSchema):
    name: str = Field(min_length=1, max_length=120)
    species: str = Field(min_length=1, max_length=120)
    status: ChargeStatus = ChargeStatus.planned
    volume_l: float = Field(default=1.0, gt=0)
    reactor_id: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator('name', 'species')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('notes')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ChargeCreate(ChargePayload):
    pass


class ChargeUpdate(ChargePayload):
    pass


class ChargeStatusUpdate(AppSchema):
    status: ChargeStatus


class ChargeRead(AppSchema):
    id: int
    name: str
    species: str
    status: ChargeStatus
    volume_l: float
    reactor_id: int | None
    start_date: date
    notes: str | None


class ReactorPayload(AppSchema):
    name: str = Field(min_length=1, max_length=120)
    reactor_type: str = Field(min_length=1, max_length=120)
    status: ReactorStatus = ReactorStatus.online
    volume_l: float = Field(default=1.0, gt=0)
    location: str | None = Field(default=None, max_length=160)
    last_cleaned_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator('name', 'reactor_type')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('location', 'notes')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ReactorCreate(ReactorPayload):
    pass


class ReactorUpdate(ReactorPayload):
    pass


class ReactorStatusUpdate(AppSchema):
    status: ReactorStatus


class ReactorRead(AppSchema):
    id: int
    name: str
    reactor_type: str
    status: ReactorStatus
    volume_l: float
    location: str | None
    last_cleaned_at: datetime | None
    notes: str | None


class ReactorTwinPayload(AppSchema):
    culture_type: str | None = Field(default=None, max_length=160)
    strain: str | None = Field(default=None, max_length=160)
    medium_recipe: str | None = Field(default=None, max_length=255)
    inoculated_at: datetime | None = None
    current_phase: ReactorPhase = ReactorPhase.growth
    target_ph_min: float | None = Field(default=None, ge=0, le=14)
    target_ph_max: float | None = Field(default=None, ge=0, le=14)
    target_temp_min: float | None = Field(default=None, ge=-20, le=150)
    target_temp_max: float | None = Field(default=None, ge=-20, le=150)
    target_light_min: float | None = Field(default=None, ge=0, le=100000)
    target_light_max: float | None = Field(default=None, ge=0, le=100000)
    target_flow_min: float | None = Field(default=None, ge=0, le=100000)
    target_flow_max: float | None = Field(default=None, ge=0, le=100000)
    expected_harvest_window_start: datetime | None = None
    expected_harvest_window_end: datetime | None = None
    contamination_state: ReactorContaminationState | None = None
    technical_state: ReactorTechnicalState = ReactorTechnicalState.nominal
    biological_state: ReactorBiologicalState = ReactorBiologicalState.unknown
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator('culture_type', 'strain', 'medium_recipe', 'notes')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode='after')
    def validate_reactor_ranges(self) -> 'ReactorTwinPayload':
        _validate_optional_range(self.target_ph_min, self.target_ph_max, 'target_ph')
        _validate_optional_range(self.target_temp_min, self.target_temp_max, 'target_temp')
        _validate_optional_range(self.target_light_min, self.target_light_max, 'target_light')
        _validate_optional_range(self.target_flow_min, self.target_flow_max, 'target_flow')
        if (
            self.expected_harvest_window_start is not None
            and self.expected_harvest_window_end is not None
            and self.expected_harvest_window_start > self.expected_harvest_window_end
        ):
            raise ValueError('expected_harvest_window_start must be before expected_harvest_window_end')
        return self


class ReactorTwinCreate(ReactorTwinPayload):
    reactor_id: int = Field(ge=1)


class ReactorTwinUpdate(ReactorTwinPayload):
    pass


class ReactorTwinPhaseUpdate(AppSchema):
    current_phase: ReactorPhase


class ReactorTwinStateUpdate(AppSchema):
    technical_state: ReactorTechnicalState
    biological_state: ReactorBiologicalState
    contamination_state: ReactorContaminationState | None = None


class ReactorEventPayload(AppSchema):
    event_type: ReactorEventType
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    severity: AlertSeverity | None = None
    phase_snapshot: ReactorPhase | None = None

    @field_validator('title')
    @classmethod
    def normalize_required_title(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('description')
    @classmethod
    def normalize_optional_description(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ReactorEventCreate(ReactorEventPayload):
    pass


class TelemetryValueCreate(AppSchema):
    reactor_id: int = Field(ge=1)
    sensor_type: TelemetrySensorType
    value: float
    unit: str = Field(min_length=1, max_length=40)
    source: TelemetrySource = TelemetrySource.manual
    timestamp: datetime | None = None

    @field_validator('unit')
    @classmethod
    def normalize_required_unit(cls, value: str) -> str:
        return _normalize_required_text(value)


class TelemetryValueRead(AppSchema):
    id: int
    reactor_id: int
    reactor_name: str | None = None
    sensor_type: TelemetrySensorType
    value: float
    unit: str
    source: TelemetrySource
    timestamp: datetime
    created_at: datetime


class DeviceNodePayload(AppSchema):
    name: str = Field(min_length=1, max_length=160)
    node_id: str | None = Field(default=None, min_length=1, max_length=120)
    node_type: DeviceNodeType
    status: DeviceNodeStatus = DeviceNodeStatus.online
    last_seen_at: datetime | None = None
    firmware_version: str | None = Field(default=None, max_length=80)
    reactor_id: int | None = Field(default=None, ge=1)

    @field_validator('name', 'node_id')
    @classmethod
    def normalize_node_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required_text(value)

    @field_validator('firmware_version')
    @classmethod
    def normalize_optional_version(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class DeviceNodeCreate(DeviceNodePayload):
    pass


class DeviceNodeUpdate(AppSchema):
    node_id: str | None = Field(default=None, min_length=1, max_length=120)
    status: DeviceNodeStatus | None = None
    last_seen_at: datetime | None = None
    firmware_version: str | None = Field(default=None, max_length=80)
    reactor_id: int | None = Field(default=None, ge=1)

    @field_validator('node_id')
    @classmethod
    def normalize_optional_node_id(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator('firmware_version')
    @classmethod
    def normalize_optional_version(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class DeviceNodeRead(AppSchema):
    id: int
    name: str
    node_id: str | None
    node_type: DeviceNodeType
    status: DeviceNodeStatus
    last_seen_at: datetime
    firmware_version: str | None
    reactor_id: int | None
    reactor_name: str | None = None
    created_at: datetime
    updated_at: datetime


class ReactorSetpointPayload(AppSchema):
    parameter: ReactorControlParameter
    target_value: float
    min_value: float | None = None
    max_value: float | None = None
    mode: ReactorSetpointMode = ReactorSetpointMode.manual

    @model_validator(mode='after')
    def validate_range(self) -> 'ReactorSetpointPayload':
        _validate_optional_range(self.min_value, self.max_value, 'setpoint')
        return self


class ReactorSetpointCreate(ReactorSetpointPayload):
    pass


class ReactorSetpointUpdate(AppSchema):
    target_value: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    mode: ReactorSetpointMode | None = None

    @model_validator(mode='after')
    def validate_range(self) -> 'ReactorSetpointUpdate':
        if self.min_value is not None or self.max_value is not None:
            _validate_optional_range(self.min_value, self.max_value, 'setpoint')
        return self


class ReactorSetpointRead(AppSchema):
    id: int
    reactor_id: int
    reactor_name: str | None = None
    parameter: ReactorControlParameter
    target_value: float
    min_value: float | None
    max_value: float | None
    mode: ReactorSetpointMode
    updated_at: datetime


class ReactorCommandCreate(AppSchema):
    command_type: ReactorCommandType


class ReactorCommandRead(AppSchema):
    id: int
    reactor_id: int
    reactor_name: str | None = None
    command_type: ReactorCommandType
    status: ReactorCommandStatus
    blocked_reason: str | None = None
    command_uid: str
    published_at: datetime | None = None
    acknowledged_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    last_error: str | None = None
    timeout_at: datetime | None = None
    ack_payload: dict | None = None
    created_at: datetime
    updated_at: datetime


class MQTTAckPayload(AppSchema):
    command_id: int | None = None
    command_uid: str | None = Field(default=None, min_length=1, max_length=64)
    status: MQTTAckStatus = MQTTAckStatus.ok
    error: str | None = Field(default=None, max_length=400)
    received_at: datetime | None = None


class MQTTTelemetryPayload(AppSchema):
    value: float
    unit: str = Field(min_length=1, max_length=40)
    timestamp: datetime | None = None
    source: TelemetrySource = TelemetrySource.device
    node_id: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator('unit')
    @classmethod
    def normalize_required_unit(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('node_id')
    @classmethod
    def normalize_optional_node_id(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class MQTTNodeStatusPayload(AppSchema):
    name: str | None = Field(default=None, max_length=160)
    reactor_id: int | None = Field(default=None, ge=1)
    node_type: DeviceNodeType = DeviceNodeType.env_control
    status: DeviceNodeStatus = DeviceNodeStatus.online
    firmware_version: str | None = Field(default=None, max_length=80)
    last_seen_at: datetime | None = None

    @field_validator('name', 'firmware_version')
    @classmethod
    def normalize_optional_text_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class MQTTHeartbeatPayload(AppSchema):
    reactor_id: int | None = Field(default=None, ge=1)
    node_type: DeviceNodeType = DeviceNodeType.env_control
    firmware_version: str | None = Field(default=None, max_length=80)
    last_seen_at: datetime | None = None

    @field_validator('firmware_version')
    @classmethod
    def normalize_optional_firmware(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class MQTTBridgeStatusRead(AppSchema):
    enabled: bool
    dependency_available: bool
    connected: bool
    broker_host: str
    broker_port: int
    client_id: str
    topic_prefix: str
    publish_commands: bool
    last_message_at: datetime | None = None
    last_error: str | None = None


class SensorPayload(AppSchema):
    name: str = Field(min_length=1, max_length=120)
    sensor_type: SensorType
    unit: str = Field(min_length=1, max_length=40)
    status: SensorStatus = SensorStatus.active
    reactor_id: int | None = Field(default=None, ge=1)
    location: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator('name', 'unit')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('location', 'notes')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SensorCreate(SensorPayload):
    pass


class SensorUpdate(SensorPayload):
    pass


class SensorStatusUpdate(AppSchema):
    status: SensorStatus


class SensorRead(AppSchema):
    id: int
    name: str
    sensor_type: SensorType
    unit: str
    status: SensorStatus
    reactor_id: int | None
    location: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    reactor_name: str | None = None
    last_value: float | None = None
    last_recorded_at: datetime | None = None
    last_value_source: str | None = None


class SensorOverviewRead(SensorRead):
    pass


class SensorValueCreate(AppSchema):
    value: float
    recorded_at: datetime | None = None
    source: str | None = Field(default=None, max_length=80)

    @field_validator('source')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SensorValueRead(AppSchema):
    id: int
    sensor_id: int
    value: float
    source: str | None
    recorded_at: datetime


class AssetPayload(AppSchema):
    name: str = Field(min_length=1, max_length=160)
    asset_type: AssetType
    category: str = Field(min_length=1, max_length=80)
    status: AssetStatus = AssetStatus.active
    location: str = Field(min_length=1, max_length=160)
    zone: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    manufacturer: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=4000)
    maintenance_notes: str | None = Field(default=None, max_length=4000)
    last_maintenance_at: datetime | None = None
    next_maintenance_at: datetime | None = None
    wiki_ref: str | None = Field(default=None, max_length=255)

    @field_validator('name', 'category', 'location')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('zone', 'serial_number', 'manufacturer', 'model', 'notes', 'maintenance_notes', 'wiki_ref')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class AssetCreate(AssetPayload):
    pass


class AssetUpdate(AssetPayload):
    pass


class AssetStatusUpdate(AppSchema):
    status: AssetStatus


class InventoryPayload(AppSchema):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    status: InventoryStatus = InventoryStatus.available
    quantity: float = Field(ge=0, le=999999999.999)
    unit: str = Field(min_length=1, max_length=40)
    min_quantity: float | None = Field(default=None, ge=0, le=999999999.999)
    location: str = Field(min_length=1, max_length=160)
    zone: str | None = Field(default=None, max_length=120)
    supplier: str | None = Field(default=None, max_length=160)
    sku: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=4000)
    asset_id: int | None = Field(default=None, ge=1)
    wiki_ref: str | None = Field(default=None, max_length=255)
    last_restocked_at: datetime | None = None
    expiry_date: date | None = None

    @field_validator('name', 'category', 'unit', 'location')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('zone', 'supplier', 'sku', 'notes', 'wiki_ref')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode='after')
    def validate_min_quantity(self) -> 'InventoryPayload':
        if self.min_quantity is not None and self.min_quantity < 0:
            raise ValueError('min_quantity must be greater than or equal to 0')
        return self


class InventoryCreate(InventoryPayload):
    pass


class InventoryUpdate(InventoryPayload):
    pass


class InventoryStatusUpdate(AppSchema):
    status: InventoryStatus


class LabelPayload(AppSchema):
    label_code: str | None = Field(default=None, min_length=3, max_length=80)
    label_type: LabelType = LabelType.qr
    target_type: LabelTargetType
    target_id: int = Field(ge=1)
    display_name: str | None = Field(default=None, max_length=160)
    location_snapshot: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=4000)
    is_active: bool = True

    @field_validator('label_code')
    @classmethod
    def normalize_label_code(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_text(value)
        return normalized.upper() if normalized else None

    @field_validator('display_name', 'location_snapshot', 'note')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class LabelCreate(LabelPayload):
    pass


class LabelUpdate(LabelPayload):
    pass


class LabelActiveUpdate(AppSchema):
    is_active: bool


class UserPayload(AppSchema):
    username: str = Field(min_length=3, max_length=80)
    display_name: str | None = Field(default=None, max_length=160)
    email: str | None = Field(default=None, max_length=160)
    role: UserRole = UserRole.viewer
    is_active: bool = True
    note: str | None = Field(default=None, max_length=4000)

    @field_validator('username')
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return _normalize_required_text(value).lower()

    @field_validator('display_name', 'email', 'note')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_text(value)
        if normalized and '@' in normalized:
            return normalized.lower()
        return normalized


class UserCreate(UserPayload):
    password: str = Field(min_length=8, max_length=256)


class UserUpdate(UserPayload):
    pass


class UserRoleUpdate(AppSchema):
    role: UserRole


class UserActiveUpdate(AppSchema):
    is_active: bool


class UserPasswordUpdate(AppSchema):
    password: str = Field(min_length=8, max_length=256)


class AuthLoginRequest(AppSchema):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)

    @field_validator('username')
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return _normalize_required_text(value).lower()


class TaskPayload(AppSchema):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus = TaskStatus.open
    priority: TaskPriority = TaskPriority.normal
    due_at: datetime | None = None
    charge_id: int | None = Field(default=None, ge=1)
    reactor_id: int | None = Field(default=None, ge=1)
    asset_id: int | None = Field(default=None, ge=1)

    @field_validator('title')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('description')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class TaskCreate(TaskPayload):
    pass


class TaskUpdate(TaskPayload):
    pass


class TaskStatusUpdate(AppSchema):
    status: TaskStatus


class TaskRead(AppSchema):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_at: datetime | None
    charge_id: int | None
    reactor_id: int | None
    asset_id: int | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None
    asset_name: str | None = None


class AlertCreate(AppSchema):
    title: str = Field(min_length=1, max_length=160)
    message: str = Field(min_length=1, max_length=4000)
    severity: AlertSeverity = AlertSeverity.warning
    status: AlertStatus = AlertStatus.open
    source_type: AlertSourceType = AlertSourceType.manual
    source_id: int | None = Field(default=None, ge=1)

    @field_validator('title', 'message')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)


class AlertRead(AppSchema):
    id: int
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    source_type: AlertSourceType
    source_id: int | None
    created_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None


class PhotoPayload(AppSchema):
    title: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=4000)
    charge_id: int | None = Field(default=None, ge=1)
    reactor_id: int | None = Field(default=None, ge=1)
    asset_id: int | None = Field(default=None, ge=1)
    uploaded_by: str | None = Field(default=None, max_length=120)
    captured_at: datetime | None = None

    @field_validator('title', 'notes', 'uploaded_by')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class PhotoUploadData(PhotoPayload):
    pass


class PhotoUpdate(PhotoPayload):
    pass


class VisionAnalysisRead(AppSchema):
    id: int
    photo_id: int
    reactor_id: int | None
    analysis_type: str
    status: str
    result: dict[str, Any]
    confidence: float | None
    error: str | None
    created_at: datetime


class ReactorHealthStatus(str, Enum):
    nominal = 'nominal'
    attention = 'attention'
    warning = 'warning'
    incident = 'incident'
    unknown = 'unknown'


class ReactorHealthSignalSeverity(str, Enum):
    info = 'info'
    attention = 'attention'
    warning = 'warning'
    incident = 'incident'


class ReactorHealthSignalRead(AppSchema):
    code: str
    severity: ReactorHealthSignalSeverity
    source: str
    message: str


class ReactorHealthAssessmentRead(AppSchema):
    id: int
    reactor_id: int
    reactor_name: str | None = None
    status: ReactorHealthStatus
    summary: str
    signals: list[ReactorHealthSignalRead]
    source_telemetry_at: datetime | None
    source_vision_analysis_id: int | None
    source_incident_count: int
    assessed_at: datetime
    created_at: datetime


class PhotoRead(AppSchema):
    id: int
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    storage_path: str
    title: str | None
    notes: str | None
    charge_id: int | None
    reactor_id: int | None
    asset_id: int | None
    created_at: datetime
    uploaded_by: str | None
    captured_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None
    asset_name: str | None = None
    file_url: str
    latest_vision: VisionAnalysisRead | None = None


class ReactorEventRead(AppSchema):
    id: int
    reactor_id: int
    reactor_name: str | None = None
    event_type: ReactorEventType
    title: str
    description: str | None
    severity: AlertSeverity | None
    phase_snapshot: ReactorPhase | None
    created_at: datetime
    created_by_user_id: int | None
    created_by_username: str | None = None


class ReactorTwinRead(AppSchema):
    id: int | None
    is_configured: bool = True
    reactor_id: int
    reactor_name: str
    reactor_type: str
    reactor_status: ReactorStatus
    reactor_volume_l: float
    reactor_location: str | None
    culture_type: str | None
    strain: str | None
    medium_recipe: str | None
    inoculated_at: datetime | None
    current_phase: ReactorPhase
    target_ph_min: float | None
    target_ph_max: float | None
    target_temp_min: float | None
    target_temp_max: float | None
    target_light_min: float | None
    target_light_max: float | None
    target_flow_min: float | None
    target_flow_max: float | None
    expected_harvest_window_start: datetime | None
    expected_harvest_window_end: datetime | None
    contamination_state: ReactorContaminationState | None
    technical_state: ReactorTechnicalState
    biological_state: ReactorBiologicalState
    notes: str | None
    created_at: datetime
    updated_at: datetime
    current_charge: ChargeRead | None = None
    sensor_count: int = 0
    open_task_count: int = 0
    open_alert_count: int = 0
    photo_count: int = 0
    latest_event: ReactorEventRead | None = None
    latest_vision: VisionAnalysisRead | None = None
    latest_health: ReactorHealthAssessmentRead | None = None


class ReactorTwinDetailRead(ReactorTwinRead):
    recent_events: list[ReactorEventRead]
    open_tasks: list[TaskRead]
    recent_alerts: list[AlertRead]
    recent_photos: list[PhotoRead]
    recent_sensors: list[SensorRead]


class ReactorTelemetryOverviewRead(AppSchema):
    reactor_id: int
    reactor_name: str
    latest_temp: float | None = None
    latest_temp_unit: str | None = None
    latest_ph: float | None = None
    latest_ph_unit: str | None = None
    last_telemetry_at: datetime | None = None


class AssetRead(AppSchema):
    id: int
    name: str
    asset_type: AssetType
    category: str
    status: AssetStatus
    location: str
    zone: str | None
    serial_number: str | None
    manufacturer: str | None
    model: str | None
    notes: str | None
    maintenance_notes: str | None
    last_maintenance_at: datetime | None
    next_maintenance_at: datetime | None
    wiki_ref: str | None
    created_at: datetime
    updated_at: datetime
    open_task_count: int = 0
    photo_count: int = 0


class AssetDetailRead(AssetRead):
    open_tasks: list[TaskRead]
    recent_photos: list[PhotoRead]


class AssetOverviewRead(AppSchema):
    active_assets: int
    assets_in_maintenance: int
    assets_in_error: int
    upcoming_maintenance_assets: list[AssetRead]


class InventoryRead(AppSchema):
    id: int
    name: str
    category: str
    status: InventoryStatus
    quantity: float
    unit: str
    min_quantity: float | None
    location: str
    zone: str | None
    supplier: str | None
    sku: str | None
    notes: str | None
    asset_id: int | None
    asset_name: str | None = None
    wiki_ref: str | None
    last_restocked_at: datetime | None
    expiry_date: date | None
    created_at: datetime
    updated_at: datetime
    is_low_stock: bool
    is_out_of_stock: bool
    needs_restock: bool


class InventoryOverviewRead(AppSchema):
    total_items: int
    low_stock_items: int
    out_of_stock_items: int
    critical_items: list[InventoryRead]


class LabelRead(AppSchema):
    id: int
    label_code: str
    label_type: LabelType
    target_type: LabelTargetType
    target_id: int
    display_name: str | None
    location_snapshot: str | None
    note: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    target_name: str | None = None
    target_location: str | None = None
    target_status: str | None = None
    scan_path: str
    scan_url: str
    target_manager_path: str
    target_manager_url: str
    qr_path: str
    qr_url: str


class LabelTargetRead(AppSchema):
    label: LabelRead
    asset: AssetRead | None = None
    inventory_item: InventoryRead | None = None


class LabelOverviewRead(AppSchema):
    labeled_assets: int
    labeled_inventory_items: int
    recent_labels: list[LabelRead]


class UserRead(AppSchema):
    id: int
    username: str
    display_name: str | None
    email: str | None
    role: UserRole
    is_active: bool
    auth_source: str
    note: str | None
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None


class AuthLoginResponse(AppSchema):
    access_token: str
    token_type: str = 'bearer'
    user: UserRead


class PhotoAnalysisStatusRead(AppSchema):
    photo_id: int
    status: str
    detail: str
    latest_vision: VisionAnalysisRead | None = None


class ABrainStatusRead(AppSchema):
    connected: bool
    mode: str
    base_url: str
    timeout_seconds: float
    fallback_available: bool
    note: str


class ABrainPresetRead(AppSchema):
    id: ABrainPreset
    title: str
    description: str
    default_question: str
    default_sections: list[ABrainContextSection]


class ABrainReferenceRead(AppSchema):
    entity_type: str
    entity_id: int
    label: str


class ABrainSummaryCountsRead(AppSchema):
    open_tasks: int
    overdue_tasks: int
    due_today_tasks: int
    critical_alerts: int
    open_alerts: int
    sensor_attention: int
    active_charges: int
    reactors_online: int
    recent_photos: int


class ABrainTaskContextItemRead(AppSchema):
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None


class ABrainAlertContextItemRead(AppSchema):
    id: int
    title: str
    severity: AlertSeverity
    status: AlertStatus
    source_type: AlertSourceType
    created_at: datetime


class ABrainSensorAttentionItemRead(AppSchema):
    id: int
    name: str
    status: SensorStatus
    reactor_name: str | None = None
    last_recorded_at: datetime | None = None
    last_value: float | None = None
    attention_reason: str


class ABrainChargeContextItemRead(AppSchema):
    id: int
    name: str
    species: str
    status: ChargeStatus


class ABrainReactorContextItemRead(AppSchema):
    id: int
    name: str
    status: ReactorStatus
    open_task_count: int
    health_status: ReactorHealthStatus | None = None
    health_summary: str | None = None
    health_assessed_at: datetime | None = None


class ABrainPhotoContextItemRead(AppSchema):
    id: int
    title: str | None
    created_at: datetime
    captured_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None
    vision_health_label: str | None = None
    vision_green_ratio: float | None = None
    vision_brown_ratio: float | None = None
    vision_confidence: float | None = None


class ABrainContextRead(AppSchema):
    generated_at: datetime
    included_sections: list[ABrainContextSection]
    summary: ABrainSummaryCountsRead
    tasks: list[ABrainTaskContextItemRead] | None = None
    alerts: list[ABrainAlertContextItemRead] | None = None
    sensors: list[ABrainSensorAttentionItemRead] | None = None
    charges: list[ABrainChargeContextItemRead] | None = None
    reactors: list[ABrainReactorContextItemRead] | None = None
    photos: list[ABrainPhotoContextItemRead] | None = None


class ABrainQueryRequest(AppSchema):
    question: str = Field(min_length=1, max_length=1000)
    preset: ABrainPreset | None = None
    include_context_sections: list[ABrainContextSection] | None = None

    @field_validator('question')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)


class ABrainQueryResponse(AppSchema):
    question: str
    preset: ABrainPreset | None
    mode: str
    fallback_used: bool
    summary: str
    highlights: list[str]
    recommended_actions: list[str]
    referenced_entities: list[ABrainReferenceRead]
    used_context_sections: list[ABrainContextSection]
    note: str | None = None
    trace_id: str | None = None


class ABrainActionRiskLevel(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'


class ABrainActionDomain(str, Enum):
    operations = 'operations'
    reactor = 'reactor'
    safety = 'safety'
    maintenance = 'maintenance'
    vision = 'vision'
    scheduler = 'scheduler'


class ABrainActionDescriptor(AppSchema):
    name: str
    description: str
    domain: ABrainActionDomain
    risk_level: ABrainActionRiskLevel
    requires_approval: bool
    allowed_roles: list[str]
    arguments: dict[str, str] = Field(default_factory=dict)
    guarded_by: list[str] = Field(default_factory=list)
    notes: str | None = None


class ABrainActionCatalogRead(AppSchema):
    contract_version: str
    generated_at: datetime
    actions: list[ABrainActionDescriptor]


class ABrainAdapterTelemetrySummary(AppSchema):
    sensor_type: str
    latest_value: float | None = None
    unit: str | None = None
    last_at: datetime | None = None
    in_range: bool | None = None


class ABrainAdapterReactorContext(AppSchema):
    id: int
    name: str
    status: ReactorStatus
    phase: ReactorPhase | None = None
    technical_state: ReactorTechnicalState | None = None
    biological_state: ReactorBiologicalState | None = None
    health_status: ReactorHealthStatus | None = None
    health_summary: str | None = None
    health_assessed_at: datetime | None = None
    open_task_count: int = 0
    open_incident_count: int = 0
    telemetry: list[ABrainAdapterTelemetrySummary] = Field(default_factory=list)
    latest_vision_label: str | None = None
    latest_vision_confidence: float | None = None


class ABrainAdapterOperationsContext(AppSchema):
    overdue_tasks: list[ABrainTaskContextItemRead] = Field(default_factory=list)
    critical_alerts: list[ABrainAlertContextItemRead] = Field(default_factory=list)
    blocked_command_count: int = 0
    failed_command_count: int = 0
    due_calibration_count: int = 0
    overdue_maintenance_count: int = 0
    open_safety_incident_count: int = 0


class ABrainAdapterResourceContextItem(AppSchema):
    kind: str
    id: int
    name: str
    detail: str | None = None


class ABrainAdapterResourceContext(AppSchema):
    low_stock: list[ABrainAdapterResourceContextItem] = Field(default_factory=list)
    out_of_stock: list[ABrainAdapterResourceContextItem] = Field(default_factory=list)
    assets_attention: list[ABrainAdapterResourceContextItem] = Field(default_factory=list)
    offline_nodes: list[ABrainAdapterResourceContextItem] = Field(default_factory=list)


class ABrainAdapterScheduleContext(AppSchema):
    active_schedule_count: int = 0
    recent_failed_run_count: int = 0
    schedules: list[ABrainAdapterResourceContextItem] = Field(default_factory=list)


class ABrainAdapterContextRead(AppSchema):
    generated_at: datetime
    contract_version: str
    mode: str
    fallback_used: bool
    summary: ABrainSummaryCountsRead
    reactors: list[ABrainAdapterReactorContext] = Field(default_factory=list)
    operations: ABrainAdapterOperationsContext
    resources: ABrainAdapterResourceContext
    schedule: ABrainAdapterScheduleContext
    photos: list[ABrainPhotoContextItemRead] = Field(default_factory=list)


class ABrainAdapterRecommendedAction(AppSchema):
    action: str
    target: str | None = None
    reason: str
    risk_level: ABrainActionRiskLevel
    requires_approval: bool
    blocked: bool = False
    blocked_reason: str | None = None


class ABrainAdapterQueryRequest(AppSchema):
    question: str = Field(min_length=1, max_length=1000)
    preset: ABrainPreset | None = None
    include_context_sections: list[ABrainContextSection] | None = None
    dry_run: bool = True

    @field_validator('question')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)


class ABrainAdapterResponse(AppSchema):
    question: str
    preset: ABrainPreset | None
    mode: str
    fallback_used: bool
    contract_version: str
    trace_id: str | None = None
    summary: str
    highlights: list[str] = Field(default_factory=list)
    recommended_actions: list[ABrainAdapterRecommendedAction] = Field(default_factory=list)
    blocked_actions: list[ABrainAdapterRecommendedAction] = Field(default_factory=list)
    approval_required: bool = False
    policy_decision: str | None = None
    used_context_sections: list[ABrainContextSection] = Field(default_factory=list)
    referenced_entities: list[ABrainReferenceRead] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ABrainReasoningMode(str, Enum):
    reactor_daily_overview = 'reactor_daily_overview'
    incident_review = 'incident_review'
    maintenance_suggestions = 'maintenance_suggestions'
    schedule_runtime_review = 'schedule_runtime_review'
    cross_domain_overview = 'cross_domain_overview'


class ABrainReasoningPrioritizedEntity(AppSchema):
    entity_type: str
    entity_id: int | str | None = None
    label: str
    reason: str | None = None
    severity: str | None = None


class ABrainReasoningCheck(AppSchema):
    check: str
    target: str | None = None
    reason: str | None = None


class ABrainReasoningRequest(AppSchema):
    mode: ABrainReasoningMode
    question: str | None = Field(default=None, max_length=1000)
    include_context_sections: list[ABrainContextSection] | None = None
    dry_run: bool = True

    @field_validator('question')
    @classmethod
    def normalize_optional_question(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ABrainReasoningResponse(AppSchema):
    reasoning_mode: ABrainReasoningMode
    question: str | None = None
    mode: str
    fallback_used: bool
    contract_version: str
    trace_id: str | None = None
    summary: str
    highlights: list[str] = Field(default_factory=list)
    prioritized_entities: list[ABrainReasoningPrioritizedEntity] = Field(default_factory=list)
    recommended_actions: list[ABrainAdapterRecommendedAction] = Field(default_factory=list)
    recommended_checks: list[ABrainReasoningCheck] = Field(default_factory=list)
    approval_required_actions: list[ABrainAdapterRecommendedAction] = Field(default_factory=list)
    blocked_or_deferred_actions: list[ABrainAdapterRecommendedAction] = Field(default_factory=list)
    used_context_sections: list[ABrainContextSection] = Field(default_factory=list)
    referenced_entities: list[ABrainReferenceRead] = Field(default_factory=list)
    policy_decision: str | None = None
    notes: list[str] = Field(default_factory=list)


class ABrainExecutionStatus(str, Enum):
    executed = 'executed'
    pending_approval = 'pending_approval'
    blocked = 'blocked'
    rejected = 'rejected'
    failed = 'failed'


class ABrainExecuteRequest(AppSchema):
    action: str = Field(min_length=1, max_length=120)
    params: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = Field(default=None, max_length=120)
    source: str | None = Field(default=None, max_length=60)
    reason: str | None = Field(default=None, max_length=2000)
    requested_via: str | None = Field(default=None, max_length=40)
    approve: bool = False

    @field_validator('action')
    @classmethod
    def normalize_action(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('reason')
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ABrainExecutionResult(AppSchema):
    action: str
    status: ABrainExecutionStatus
    blocked_reason: str | None = None
    requires_approval: bool = False
    risk_level: ABrainActionRiskLevel | None = None
    trace_id: str | None = None
    executed_by: str | None = None
    source: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    log_id: int | None = None
    approval_request_id: int | None = None
    created_at: datetime


class ABrainExecutionLogRead(AppSchema):
    id: int
    action: str
    params: dict[str, Any]
    status: ABrainExecutionStatus
    blocked_reason: str | None = None
    source: str | None = None
    executed_by: str | None = None
    trace_id: str | None = None
    approval_request_id: int | None = None
    result: dict[str, Any]
    created_at: datetime


class ApprovalRequestStatus(str, Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    executed = 'executed'
    failed = 'failed'
    cancelled = 'cancelled'


class ApprovalRequestSource(str, Enum):
    abrain = 'abrain'
    local_dev_fallback = 'local_dev_fallback'
    operator = 'operator'


class ApprovalRequestVia(str, Enum):
    adapter = 'adapter'
    legacy_query = 'legacy_query'
    future_mcp = 'future_mcp'
    mcp = 'mcp'
    ros = 'ros'
    operator_ui = 'operator_ui'


class ApprovalDecisionPayload(AppSchema):
    decision_note: str | None = Field(default=None, max_length=2000)

    @field_validator('decision_note')
    @classmethod
    def normalize_decision_note(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ApprovalRequestRead(AppSchema):
    id: int
    action_name: str
    action_params: dict[str, Any]
    requested_by_source: ApprovalRequestSource
    requested_by_user_id: int | None = None
    requested_by_username: str | None = None
    requested_via: ApprovalRequestVia
    trace_id: str | None = None
    risk_level: ABrainActionRiskLevel | None = None
    status: ApprovalRequestStatus
    reason: str | None = None
    decision_note: str | None = None
    approval_required: bool = True
    approved_by_user_id: int | None = None
    approved_by_username: str | None = None
    decided_at: datetime | None = None
    executed_execution_log_id: int | None = None
    blocked_reason: str | None = None
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime


class ApprovalOverviewRead(AppSchema):
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    executed: int = 0
    failed: int = 0
    cancelled: int = 0
    high_risk_pending: int = 0


class TraceContextStatus(str, Enum):
    open = 'open'
    completed = 'completed'
    failed = 'failed'


class TraceContextSource(str, Enum):
    abrain = 'abrain'
    local = 'local'
    operator = 'operator'
    api = 'api'


class TraceContextRead(AppSchema):
    trace_id: str
    source: TraceContextSource
    status: TraceContextStatus
    root_query: str | None = None
    summary: str | None = None
    context_snapshot: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    execution_count: int = 0
    approval_count: int = 0
    pending_approval_count: int = 0


class TraceTimelineEventKind(str, Enum):
    query = 'query'
    approval = 'approval'
    execution = 'execution'


class TraceTimelineEvent(AppSchema):
    kind: TraceTimelineEventKind
    created_at: datetime
    label: str
    status: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class TraceContextDetailRead(TraceContextRead):
    timeline: list[TraceTimelineEvent] = Field(default_factory=list)
    executions: list[ABrainExecutionLogRead] = Field(default_factory=list)
    approvals: list[ApprovalRequestRead] = Field(default_factory=list)


class RulePayload(AppSchema):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    is_enabled: bool = True
    trigger_type: RuleTriggerType
    condition_type: RuleConditionType
    condition_config: dict[str, Any] = Field(default_factory=dict)
    action_type: RuleActionType
    action_config: dict[str, Any] = Field(default_factory=dict)

    @field_validator('name')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('description')
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode='after')
    def validate_rule_payload(self):
        _validate_rule_configuration(
            self.trigger_type,
            self.condition_type,
            self.condition_config,
            self.action_type,
            self.action_config,
        )
        return self


class RuleCreate(RulePayload):
    pass


class RuleUpdate(RulePayload):
    pass


class RuleEnabledUpdate(AppSchema):
    is_enabled: bool


class RuleRead(AppSchema):
    id: int
    name: str
    description: str | None
    is_enabled: bool
    trigger_type: RuleTriggerType
    condition_type: RuleConditionType
    condition_config: dict[str, Any]
    action_type: RuleActionType
    action_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_evaluated_at: datetime | None


class RuleExecutionRead(AppSchema):
    id: int
    rule_id: int
    rule_name: str | None = None
    status: RuleExecutionStatus
    dry_run: bool
    evaluation_summary: dict[str, Any]
    action_result: dict[str, Any]
    created_at: datetime


class RuleEvaluationResponse(AppSchema):
    rule: RuleRead
    execution: RuleExecutionRead


class EvaluateAllRulesResponse(AppSchema):
    executions: list[RuleExecutionRead]


class CalibrationRecordCreate(AppSchema):
    target_type: CalibrationTargetType
    target_id: int = Field(ge=1)
    parameter: str = Field(min_length=1, max_length=80)
    status: CalibrationStatus = CalibrationStatus.unknown
    calibrated_at: datetime | None = None
    due_at: datetime | None = None
    calibration_value: float | None = None
    reference_value: float | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator('parameter')
    @classmethod
    def normalize_parameter(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('note')
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class CalibrationRecordUpdate(AppSchema):
    status: CalibrationStatus | None = None
    calibrated_at: datetime | None = None
    due_at: datetime | None = None
    calibration_value: float | None = None
    reference_value: float | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator('note')
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class CalibrationRecordRead(AppSchema):
    id: int
    target_type: CalibrationTargetType
    target_id: int
    target_name: str | None = None
    parameter: str
    status: CalibrationStatus
    calibrated_at: datetime | None
    due_at: datetime | None
    calibration_value: float | None
    reference_value: float | None
    performed_by_user_id: int | None
    performed_by_username: str | None = None
    note: str | None
    created_at: datetime
    updated_at: datetime


class CalibrationOverviewRead(AppSchema):
    total: int
    valid: int
    due: int
    expired: int
    failed: int
    unknown: int
    due_or_expired: int


class MaintenanceRecordCreate(AppSchema):
    target_type: MaintenanceTargetType
    target_id: int = Field(ge=1)
    maintenance_type: MaintenanceType
    status: MaintenanceStatus = MaintenanceStatus.scheduled
    performed_at: datetime | None = None
    due_at: datetime | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator('note')
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class MaintenanceRecordUpdate(AppSchema):
    maintenance_type: MaintenanceType | None = None
    status: MaintenanceStatus | None = None
    performed_at: datetime | None = None
    due_at: datetime | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator('note')
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class MaintenanceRecordRead(AppSchema):
    id: int
    target_type: MaintenanceTargetType
    target_id: int
    target_name: str | None = None
    maintenance_type: MaintenanceType
    status: MaintenanceStatus
    performed_at: datetime | None
    due_at: datetime | None
    performed_by_user_id: int | None
    performed_by_username: str | None = None
    note: str | None
    created_at: datetime
    updated_at: datetime


class MaintenanceOverviewRead(AppSchema):
    total: int
    scheduled: int
    done: int
    overdue: int
    skipped: int


class SafetyIncidentCreate(AppSchema):
    reactor_id: int | None = Field(default=None, ge=1)
    device_node_id: int | None = Field(default=None, ge=1)
    asset_id: int | None = Field(default=None, ge=1)
    incident_type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.warning
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator('title')
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('description')
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SafetyIncidentUpdate(AppSchema):
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    description: str | None = Field(default=None, max_length=4000)

    @field_validator('description')
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class SafetyIncidentRead(AppSchema):
    id: int
    reactor_id: int | None
    reactor_name: str | None = None
    device_node_id: int | None
    device_node_name: str | None = None
    asset_id: int | None
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    title: str
    description: str | None
    created_at: datetime
    resolved_at: datetime | None
    created_by_user_id: int | None
    created_by_username: str | None = None


class SafetyOverviewRead(AppSchema):
    open_incidents: int
    acknowledged_incidents: int
    critical_incidents: int
    high_incidents: int
    blocked_commands: int
    calibration_expired: int
    maintenance_overdue: int


class DashboardSummaryRead(AppSchema):
    active_charges: int
    reactors_online: int
    reactors_attention: int
    reactors_harvest_ready: int
    reactors_incident_or_contamination: int
    reactors_health_nominal: int = 0
    reactors_health_attention: int = 0
    reactors_health_warning: int = 0
    reactors_health_incident: int = 0
    reactors_health_unknown: int = 0
    offline_devices: int
    active_sensors: int
    error_sensors: int
    active_assets: int
    assets_in_maintenance: int
    assets_in_error: int
    labeled_assets: int
    inventory_items: int
    inventory_low_stock: int
    inventory_out_of_stock: int
    labeled_inventory_items: int
    open_tasks: int
    due_today_tasks: int
    critical_alerts: int
    open_alerts: int
    photo_count: int
    uploads_last_7_days: int
    active_rules: int
    open_safety_incidents: int
    calibration_due_or_expired: int
    maintenance_overdue: int
    sensor_overview: list[SensorOverviewRead]
    reactor_telemetry_overview: list[ReactorTelemetryOverviewRead]
    recent_alerts: list[AlertRead]
    recent_photos: list[PhotoRead]
    recent_reactor_events: list[ReactorEventRead]
    recent_rule_executions: list[RuleExecutionRead]
    upcoming_maintenance_assets: list[AssetRead]
    critical_inventory_items: list[InventoryRead]
    recent_labels: list[LabelRead]
    recent_safety_incidents: list[SafetyIncidentRead]
    message: str


def _validate_optional_range(min_value: float | None, max_value: float | None, field_name: str) -> None:
    if min_value is None or max_value is None:
        return
    if min_value > max_value:
        raise ValueError(f'{field_name}_min must be less than or equal to {field_name}_max')


def _require_config_keys(config: dict[str, Any], keys: set[str], scope: str) -> None:
    missing = sorted(key for key in keys if key not in config)
    if missing:
        raise ValueError(f'{scope} missing required keys: {", ".join(missing)}')


class ScheduleType(str, Enum):
    interval = 'interval'
    cron = 'cron'
    manual = 'manual'


class ScheduleTargetType(str, Enum):
    command = 'command'
    rule = 'rule'


class ScheduleExecutionStatus(str, Enum):
    success = 'success'
    failed = 'failed'
    skipped = 'skipped'


class SchedulePayload(AppSchema):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    schedule_type: ScheduleType
    interval_seconds: int | None = Field(default=None, ge=5, le=7 * 24 * 3600)
    cron_expr: str | None = Field(default=None, max_length=120)
    target_type: ScheduleTargetType
    target_id: int | None = Field(default=None, ge=1)
    reactor_id: int | None = Field(default=None, ge=1)
    target_params: dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator('description')
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator('cron_expr')
    @classmethod
    def normalize_cron(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode='after')
    def validate_schedule_payload(self):
        if self.schedule_type == ScheduleType.interval:
            if self.interval_seconds is None:
                raise ValueError('interval schedules require interval_seconds')
        elif self.schedule_type == ScheduleType.cron:
            if not self.cron_expr:
                raise ValueError('cron schedules require cron_expr')
        if self.target_type == ScheduleTargetType.command:
            if self.reactor_id is None:
                raise ValueError('command schedules require reactor_id')
            command_type = self.target_params.get('command_type') if isinstance(self.target_params, dict) else None
            if not command_type:
                raise ValueError('command schedules require target_params.command_type')
        if self.target_type == ScheduleTargetType.rule:
            if self.target_id is None:
                raise ValueError('rule schedules require target_id')
        return self


class ScheduleCreate(SchedulePayload):
    pass


class ScheduleUpdate(SchedulePayload):
    pass


class ScheduleEnabledUpdate(AppSchema):
    is_enabled: bool


class ScheduleRead(AppSchema):
    id: int
    name: str
    description: str | None
    schedule_type: ScheduleType
    interval_seconds: int | None
    cron_expr: str | None
    target_type: ScheduleTargetType
    target_id: int | None
    reactor_id: int | None
    target_params: dict[str, Any]
    is_enabled: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    last_status: ScheduleExecutionStatus | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class ScheduleExecutionRead(AppSchema):
    id: int
    schedule_id: int
    status: ScheduleExecutionStatus
    trigger: str
    started_at: datetime
    finished_at: datetime | None
    result: dict[str, Any]
    error: str | None


class ScheduleRunResponse(AppSchema):
    schedule: ScheduleRead
    execution: ScheduleExecutionRead


def _validate_rule_configuration(
    trigger_type: RuleTriggerType,
    condition_type: RuleConditionType,
    condition_config: dict[str, Any],
    action_type: RuleActionType,
    action_config: dict[str, Any],
) -> None:
    if trigger_type == RuleTriggerType.sensor_threshold:
        if condition_type not in {RuleConditionType.threshold_gt, RuleConditionType.threshold_lt}:
            raise ValueError('sensor_threshold supports only threshold_gt or threshold_lt')
        _require_config_keys(condition_config, {'sensor_id', 'threshold'}, 'condition_config')
    elif trigger_type == RuleTriggerType.stale_sensor:
        if condition_type != RuleConditionType.age_gt_hours:
            raise ValueError('stale_sensor supports only age_gt_hours')
        _require_config_keys(condition_config, {'hours'}, 'condition_config')
    elif trigger_type == RuleTriggerType.overdue_tasks:
        if condition_type != RuleConditionType.count_gt:
            raise ValueError('overdue_tasks supports only count_gt')
        _require_config_keys(condition_config, {'count'}, 'condition_config')
    elif trigger_type == RuleTriggerType.reactor_status:
        if condition_type != RuleConditionType.status_is:
            raise ValueError('reactor_status supports only status_is')
        _require_config_keys(condition_config, {'reactor_id', 'status'}, 'condition_config')

    if action_type == RuleActionType.create_alert:
        _require_config_keys(action_config, {'title_template', 'message_template', 'severity'}, 'action_config')
    elif action_type == RuleActionType.create_task:
        _require_config_keys(action_config, {'title_template', 'priority'}, 'action_config')
