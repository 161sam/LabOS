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


class DashboardSummaryRead(AppSchema):
    active_charges: int
    reactors_online: int
    open_alerts: int
    today_tasks: int
    active_sensors: int
    error_sensors: int
    sensor_overview: list[SensorOverviewRead]
    message: str
