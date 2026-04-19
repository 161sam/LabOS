"""Message envelope standard for cross-system messages.

Every message handed to the orchestrator must be wrapped as a
`MessageEnvelope`. The envelope carries the minimum required metadata
to make loop-prevention and source-of-truth rules machine-checkable:

- `message_id` — uuid for dedup (set once, never rewritten on hops)
- `source`    — which transport originated the message
- `ts`        — unix seconds; immutable across hops
- `kind`      — telemetry / command / event
- payload fields are intentionally minimal; domain specifics live in
  `extras` so the envelope stays stable over time.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SourceTag(str, Enum):
    mqtt = 'mqtt'
    ros = 'ros'
    labos = 'labos'


class EnvelopeKind(str, Enum):
    telemetry = 'telemetry'
    command = 'command'
    event = 'event'


def new_message_id() -> str:
    return uuid4().hex


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


class MessageEnvelope(BaseModel):
    message_id: str = Field(default_factory=new_message_id)
    source: SourceTag
    ts: int = Field(default_factory=_now_ts)
    kind: EnvelopeKind
    reactor_id: int | None = None
    node_id: str | None = None
    key: str | None = None  # sensor_type for telemetry, command_type for command
    value: Any | None = None
    unit: str | None = None
    extras: dict[str, Any] = Field(default_factory=dict)


__all__ = ['EnvelopeKind', 'MessageEnvelope', 'SourceTag', 'new_message_id']
