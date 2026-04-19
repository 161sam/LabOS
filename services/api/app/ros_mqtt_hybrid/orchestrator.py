"""Hybrid orchestrator — single cross-system routing gate.

Rules enforced:

1. Commands MUST originate from LabOS (`source=='labos'`). Envelopes
   with `kind='command'` and `source=='mqtt'` are rejected. `source=='ros'`
   commands are also rejected — ROS callbacks that want to issue a
   command must hand off to `abrain_execution.execute_action` via
   `ros_actions.dispatch_ros_command`, which will re-enter the
   orchestrator with `source='labos'` on the outbound path.
2. Telemetry routing never loops: an envelope that arrived on MQTT
   never publishes back to MQTT, and the same for ROS.
3. Duplicates (same `message_id`) are dropped.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Callable

from .envelope import EnvelopeKind, MessageEnvelope, SourceTag
from .loop_guard import LoopGuard


class HybridPolicyError(RuntimeError):
    """Raised when an envelope violates a hard hybrid rule."""


Publisher = Callable[[MessageEnvelope], None]


@dataclass
class HybridRouteResult:
    accepted: bool
    forwarded_to_mqtt: bool = False
    forwarded_to_ros: bool = False
    dropped_reason: str | None = None


@dataclass
class HybridStats:
    admitted: int = 0
    dropped_duplicate: int = 0
    forwarded_mqtt: int = 0
    forwarded_ros: int = 0
    rejected_commands: int = 0
    last_error: str | None = None
    publishers: dict[str, bool] = field(default_factory=lambda: {'mqtt': False, 'ros': False})


class HybridOrchestrator:
    def __init__(self, *, guard: LoopGuard | None = None):
        self._guard = guard or LoopGuard()
        self._mqtt_publisher: Publisher | None = None
        self._ros_publisher: Publisher | None = None
        self._stats = HybridStats()
        self._lock = Lock()

    # ---- publisher registration ----------------------------------------
    def register_mqtt_publisher(self, publisher: Publisher | None) -> None:
        with self._lock:
            self._mqtt_publisher = publisher
            self._stats.publishers['mqtt'] = publisher is not None

    def register_ros_publisher(self, publisher: Publisher | None) -> None:
        with self._lock:
            self._ros_publisher = publisher
            self._stats.publishers['ros'] = publisher is not None

    # ---- public API ----------------------------------------------------
    def publish(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if envelope.kind == EnvelopeKind.command:
            return self._publish_command(envelope)
        return self._publish_non_command(envelope)

    def publish_telemetry(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if envelope.kind != EnvelopeKind.telemetry:
            raise HybridPolicyError(
                f'publish_telemetry requires kind=telemetry, got {envelope.kind.value}'
            )
        return self._publish_non_command(envelope)

    def publish_event(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if envelope.kind != EnvelopeKind.event:
            raise HybridPolicyError(
                f'publish_event requires kind=event, got {envelope.kind.value}'
            )
        return self._publish_non_command(envelope)

    def publish_command(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if envelope.kind != EnvelopeKind.command:
            raise HybridPolicyError(
                f'publish_command requires kind=command, got {envelope.kind.value}'
            )
        return self._publish_command(envelope)

    def stats(self) -> HybridStats:
        with self._lock:
            return HybridStats(
                admitted=self._stats.admitted,
                dropped_duplicate=self._stats.dropped_duplicate,
                forwarded_mqtt=self._stats.forwarded_mqtt,
                forwarded_ros=self._stats.forwarded_ros,
                rejected_commands=self._stats.rejected_commands,
                last_error=self._stats.last_error,
                publishers=dict(self._stats.publishers),
            )

    # ---- internals -----------------------------------------------------
    def _publish_command(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if envelope.source in (SourceTag.mqtt, SourceTag.ros):
            with self._lock:
                self._stats.rejected_commands += 1
                self._stats.last_error = f'command rejected from source={envelope.source.value}'
            raise HybridPolicyError(
                f'commands cannot originate from {envelope.source.value}; '
                'use abrain_execution.execute_action to route through LabOS'
            )
        if not self._guard.admit(envelope.message_id):
            with self._lock:
                self._stats.dropped_duplicate += 1
            return HybridRouteResult(accepted=False, dropped_reason='duplicate_message_id')

        with self._lock:
            self._stats.admitted += 1
        result = HybridRouteResult(accepted=True)
        # Commands always originate from LabOS: fan out to both transports,
        # each bridge decides whether it owns the target node.
        if self._ros_publisher is not None:
            self._safe_call(self._ros_publisher, envelope, target='ros')
            result.forwarded_to_ros = True
            with self._lock:
                self._stats.forwarded_ros += 1
        if self._mqtt_publisher is not None:
            self._safe_call(self._mqtt_publisher, envelope, target='mqtt')
            result.forwarded_to_mqtt = True
            with self._lock:
                self._stats.forwarded_mqtt += 1
        return result

    def _publish_non_command(self, envelope: MessageEnvelope) -> HybridRouteResult:
        if not self._guard.admit(envelope.message_id):
            with self._lock:
                self._stats.dropped_duplicate += 1
            return HybridRouteResult(accepted=False, dropped_reason='duplicate_message_id')

        with self._lock:
            self._stats.admitted += 1

        result = HybridRouteResult(accepted=True)
        # Loop prevention: never send back to the source transport.
        if envelope.source != SourceTag.mqtt and self._mqtt_publisher is not None:
            self._safe_call(self._mqtt_publisher, envelope, target='mqtt')
            result.forwarded_to_mqtt = True
            with self._lock:
                self._stats.forwarded_mqtt += 1
        if envelope.source != SourceTag.ros and self._ros_publisher is not None:
            self._safe_call(self._ros_publisher, envelope, target='ros')
            result.forwarded_to_ros = True
            with self._lock:
                self._stats.forwarded_ros += 1
        return result

    def _safe_call(self, publisher: Publisher, envelope: MessageEnvelope, *, target: str) -> None:
        try:
            publisher(envelope)
        except Exception as exc:  # noqa: BLE001 — bridge failures must not kill the caller
            with self._lock:
                self._stats.last_error = f'{target}_publisher_error: {exc.__class__.__name__}: {exc}'


_orchestrator = HybridOrchestrator()


def get_orchestrator() -> HybridOrchestrator:
    return _orchestrator


__all__ = [
    'HybridOrchestrator',
    'HybridPolicyError',
    'HybridRouteResult',
    'HybridStats',
    'get_orchestrator',
]
