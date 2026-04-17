from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class TaskPayload(AppSchema):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus = TaskStatus.open
    priority: TaskPriority = TaskPriority.normal
    due_at: datetime | None = None
    charge_id: int | None = Field(default=None, ge=1)
    reactor_id: int | None = Field(default=None, ge=1)

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
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None


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
    created_at: datetime
    uploaded_by: str | None
    captured_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None
    file_url: str


class PhotoAnalysisStatusRead(AppSchema):
    photo_id: int
    status: str
    detail: str


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


class ABrainPhotoContextItemRead(AppSchema):
    id: int
    title: str | None
    created_at: datetime
    captured_at: datetime | None
    charge_name: str | None = None
    reactor_name: str | None = None


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


class DashboardSummaryRead(AppSchema):
    active_charges: int
    reactors_online: int
    active_sensors: int
    error_sensors: int
    open_tasks: int
    due_today_tasks: int
    critical_alerts: int
    open_alerts: int
    photo_count: int
    uploads_last_7_days: int
    sensor_overview: list[SensorOverviewRead]
    recent_alerts: list[AlertRead]
    recent_photos: list[PhotoRead]
    message: str
