from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy import Column, Index, JSON
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


class WikiPage(SQLModel, table=True):
    slug: str = Field(primary_key=True)
    title: str
    summary: Optional[str] = None
