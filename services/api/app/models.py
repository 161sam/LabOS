from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Index
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
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = 'open'
    due_date: Optional[date] = None


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    level: str = 'info'
    message: str
    status: str = 'open'
    created_at: datetime = Field(default_factory=_utcnow)


class WikiPage(SQLModel, table=True):
    slug: str = Field(primary_key=True)
    title: str
    summary: Optional[str] = None
