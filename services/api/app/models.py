from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


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
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sensor_type: str
    unit: str
    reactor_id: Optional[int] = None
    status: str = 'connected'


class SensorValue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


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
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WikiPage(SQLModel, table=True):
    slug: str = Field(primary_key=True)
    title: str
    summary: Optional[str] = None
