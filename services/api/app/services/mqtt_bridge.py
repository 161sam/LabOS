"""MQTT bridge — TRANSPORT ONLY.

Boundary Hardening V1: this module receives telemetry/node/ACK
messages and publishes reactor commands. It contains NO interpretation
or decision logic:

- incoming telemetry is persisted verbatim (after schema validation),
- incoming node status updates the device-node row,
- incoming ACKs flip the command status via `process_command_ack`,
- outgoing commands are published to the pre-computed topic.

Any logic that looks like "if telemetry X > Y then do Z" does NOT
belong here. Decisions live behind the ABrain adapter.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Callable

from pydantic import ValidationError
from sqlmodel import Session

from ..config import settings
from ..db import engine
from ..ros_mqtt_hybrid import (
    EnvelopeKind,
    HybridPolicyError,
    MessageEnvelope,
    SourceTag,
    get_orchestrator,
    new_message_id,
)
from ..schemas import (
    MQTTAckPayload,
    MQTTBridgeStatusRead,
    MQTTHeartbeatPayload,
    MQTTNodeStatusPayload,
    MQTTTelemetryPayload,
)
from . import reactor_control as reactor_control_service
from .mqtt_topics import (
    build_ack_subscription,
    build_control_topic,
    build_node_subscription,
    build_telemetry_subscription,
    get_control_channel,
    parse_ack_topic,
    parse_node_topic,
    parse_telemetry_topic,
)

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - exercised through status checks when dependency is missing.
    mqtt = None


logger = logging.getLogger(__name__)


class MQTTBridge:
    def __init__(self, session_factory: Callable[[], Session] | None = None):
        self._session_factory = session_factory or self._default_session_factory
        self._client = None
        self._connected = False
        self._started = False
        self._last_message_at: datetime | None = None
        self._last_error: str | None = None
        self._lock = Lock()

    def _default_session_factory(self) -> Session:
        return Session(engine)

    @property
    def dependency_available(self) -> bool:
        return mqtt is not None

    def start(self) -> None:
        if not settings.mqtt_enabled:
            logger.info('MQTT bridge disabled by configuration')
            return
        if mqtt is None:
            self._set_last_error('paho-mqtt dependency not installed')
            logger.warning('MQTT bridge disabled because paho-mqtt is not available')
            return
        with self._lock:
            if self._started:
                return
            try:
                client = mqtt.Client(client_id=settings.mqtt_client_id, transport='tcp')
                client.enable_logger(logger)
                client.on_connect = self._on_connect
                client.on_disconnect = self._on_disconnect
                client.on_message = self._on_message
                client.connect_async(settings.mqtt_broker_host, settings.mqtt_broker_port, keepalive=30)
                client.loop_start()
                self._client = client
                self._started = True
                self._last_error = None
            except Exception as exc:  # pragma: no cover - depends on runtime broker/network state.
                self._client = None
                self._started = False
                self._connected = False
                self._set_last_error(f'Failed to start MQTT bridge: {exc}')
                logger.warning('MQTT bridge start failed: %s', exc)

    def stop(self) -> None:
        with self._lock:
            client = self._client
            self._client = None
            self._started = False
            self._connected = False
        if client is not None:
            try:
                client.loop_stop()
                client.disconnect()
            except Exception as exc:  # pragma: no cover - best effort during shutdown.
                logger.warning('MQTT bridge stop encountered an error: %s', exc)

    def status(self) -> MQTTBridgeStatusRead:
        return MQTTBridgeStatusRead(
            enabled=settings.mqtt_enabled,
            dependency_available=self.dependency_available,
            connected=self._connected,
            broker_host=settings.mqtt_broker_host,
            broker_port=settings.mqtt_broker_port,
            client_id=settings.mqtt_client_id,
            topic_prefix=settings.mqtt_topic_prefix,
            publish_commands=settings.mqtt_publish_commands,
            last_message_at=self._last_message_at,
            last_error=self._last_error,
        )

    def publish_reactor_command(
        self,
        *,
        reactor_id: int,
        command_id: int,
        command_type: str,
        command_uid: str | None = None,
    ) -> bool | None:
        # Announce the command through the hybrid orchestrator first — the
        # orchestrator enforces "commands cannot originate from MQTT/ROS"
        # and records the routing decision. Best-effort: any registered
        # ROS publisher runs; MQTT is still dispatched below for the
        # actual wire publish.
        try:
            get_orchestrator().publish_command(
                MessageEnvelope(
                    message_id=command_uid or new_message_id(),
                    source=SourceTag.labos,
                    kind=EnvelopeKind.command,
                    reactor_id=reactor_id,
                    key=command_type,
                    extras={'command_id': command_id, 'command_uid': command_uid},
                )
            )
        except HybridPolicyError as exc:  # pragma: no cover - defensive only
            self._set_last_error(f'Hybrid orchestrator rejected command: {exc}')
            return False

        if not settings.mqtt_enabled or not settings.mqtt_publish_commands:
            return None
        client = self._client
        if mqtt is None or client is None or not self._connected:
            self._set_last_error('MQTT broker not connected for command publish')
            logger.warning('Skipping MQTT publish for command %s because bridge is not connected', command_id)
            return False
        topic = build_control_topic(settings.mqtt_topic_prefix, reactor_id=reactor_id, command_type=command_type)
        channel, action = get_control_channel(command_type)
        payload = json.dumps(
            {
                'command_id': command_id,
                'command_uid': command_uid,
                'reactor_id': reactor_id,
                'command_type': command_type,
                'channel': channel,
                'command': action,
                'source': 'labos',
                'created_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            }
        )
        try:
            info = client.publish(topic, payload, qos=0, retain=False)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                self._set_last_error(f'MQTT publish returned error code {info.rc}')
                logger.warning('MQTT publish failed for command %s with rc=%s', command_id, info.rc)
                return False
            return True
        except Exception as exc:  # pragma: no cover - depends on runtime broker/network state.
            self._set_last_error(f'MQTT publish failed: {exc}')
            logger.warning('MQTT publish raised for command %s: %s', command_id, exc)
            return False

    def publish_envelope(self, envelope: MessageEnvelope) -> None:
        """Orchestrator hook. Outbound MQTT writes are handled by the
        existing `publish_reactor_command` path; this method is a
        deliberate no-op so that orchestrator.publish_command cannot
        recurse into publish_reactor_command and create a loop."""
        return None

    def handle_message(self, topic: str, payload: bytes) -> None:
        try:
            decoded = payload.decode('utf-8')
            message = json.loads(decoded or '{}')
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._set_last_error(f'Invalid MQTT payload on {topic}: {exc}')
            logger.warning('Invalid MQTT payload on %s: %s', topic, exc)
            return

        telemetry_match = parse_telemetry_topic(topic, prefix=settings.mqtt_topic_prefix)
        if telemetry_match is not None:
            self._handle_telemetry_message(telemetry_match.reactor_id, telemetry_match.sensor_type, message)
            return

        node_match = parse_node_topic(topic, prefix=settings.mqtt_topic_prefix)
        if node_match is not None:
            self._handle_node_message(node_match.node_id, node_match.message_kind, message)
            return

        ack_match = parse_ack_topic(topic, prefix=settings.mqtt_topic_prefix)
        if ack_match is not None:
            self._handle_ack_message(ack_match.reactor_id, message)
            return

        logger.debug('Ignoring MQTT topic outside LabOS topic map: %s', topic)

    def _handle_telemetry_message(self, reactor_id: int, sensor_type: str, message: dict) -> None:
        try:
            payload = MQTTTelemetryPayload.model_validate(message)
        except ValidationError as exc:
            self._set_last_error(f'Invalid telemetry payload for reactor {reactor_id}: {exc}')
            logger.warning('Invalid MQTT telemetry payload for reactor %s: %s', reactor_id, exc)
            return

        try:
            with self._session_factory() as session:
                telemetry = reactor_control_service.create_telemetry_value_record(
                    session,
                    reactor_id=reactor_id,
                    sensor_type=sensor_type,
                    value=payload.value,
                    unit=payload.unit,
                    source=payload.source.value,
                    timestamp=payload.timestamp,
                )
                session.add(telemetry)
                session.commit()
            self._last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)
            # Announce to the hybrid orchestrator so ROS subscribers can
            # see MQTT-originated telemetry. Loop-guard + source tag in
            # the orchestrator ensure we don't re-publish back to MQTT.
            try:
                get_orchestrator().publish_telemetry(
                    MessageEnvelope(
                        source=SourceTag.mqtt,
                        kind=EnvelopeKind.telemetry,
                        reactor_id=reactor_id,
                        key=sensor_type,
                        value=payload.value,
                        unit=payload.unit,
                    )
                )
            except Exception:  # noqa: BLE001 - orchestrator failures must not affect persistence
                pass
        except Exception as exc:
            self._set_last_error(f'Failed to persist MQTT telemetry for reactor {reactor_id}: {exc}')
            logger.warning('Failed to persist MQTT telemetry for reactor %s: %s', reactor_id, exc)

    def _handle_node_message(self, node_id: str, message_kind: str, message: dict) -> None:
        try:
            if message_kind == 'status':
                payload = MQTTNodeStatusPayload.model_validate(message)
                status = payload.status.value
                name = payload.name or node_id
            else:
                payload = MQTTHeartbeatPayload.model_validate(message)
                status = 'online'
                name = node_id
        except ValidationError as exc:
            self._set_last_error(f'Invalid node payload for {node_id}: {exc}')
            logger.warning('Invalid MQTT node payload for %s: %s', node_id, exc)
            return

        try:
            with self._session_factory() as session:
                reactor_control_service.upsert_device_node_by_node_id(
                    session,
                    node_id=node_id,
                    name=name,
                    node_type=payload.node_type.value,
                    status=status,
                    last_seen_at=payload.last_seen_at,
                    firmware_version=payload.firmware_version,
                    reactor_id=payload.reactor_id,
                )
                session.commit()
            self._last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)
        except Exception as exc:
            self._set_last_error(f'Failed to persist MQTT node message for {node_id}: {exc}')
            logger.warning('Failed to persist MQTT node message for %s: %s', node_id, exc)

    def _handle_ack_message(self, reactor_id: int, message: dict) -> None:
        try:
            payload = MQTTAckPayload.model_validate(message)
        except ValidationError as exc:
            self._set_last_error(f'Invalid ACK payload for reactor {reactor_id}: {exc}')
            logger.warning('Invalid MQTT ACK payload for reactor %s: %s', reactor_id, exc)
            return

        if payload.command_id is None and payload.command_uid is None:
            self._set_last_error(f'ACK on reactor {reactor_id} missing command_id and command_uid')
            logger.warning('ACK missing identifiers for reactor %s', reactor_id)
            return

        try:
            with self._session_factory() as session:
                reactor_control_service.process_command_ack(
                    session,
                    reactor_id=reactor_id,
                    command_id=payload.command_id,
                    command_uid=payload.command_uid,
                    ack_status=payload.status.value,
                    error=payload.error,
                    received_at=payload.received_at,
                    raw_payload=message,
                )
                session.commit()
            self._last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)
        except Exception as exc:
            self._set_last_error(f'Failed to persist MQTT ACK for reactor {reactor_id}: {exc}')
            logger.warning('Failed to persist MQTT ACK for reactor %s: %s', reactor_id, exc)

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):  # pragma: no cover - runtime integration
        if reason_code == 0:
            telemetry_topic = build_telemetry_subscription(settings.mqtt_topic_prefix)
            node_topic = build_node_subscription(settings.mqtt_topic_prefix)
            ack_topic = build_ack_subscription(settings.mqtt_topic_prefix)
            client.subscribe(telemetry_topic)
            client.subscribe(node_topic)
            client.subscribe(ack_topic)
            self._connected = True
            self._last_error = None
            logger.info('MQTT bridge connected to %s:%s', settings.mqtt_broker_host, settings.mqtt_broker_port)
            logger.info('MQTT bridge subscribed to %s, %s and %s', telemetry_topic, node_topic, ack_topic)
            return
        self._connected = False
        self._set_last_error(f'MQTT connect failed with reason code {reason_code}')
        logger.warning('MQTT bridge connect failed with reason code %s', reason_code)

    def _on_disconnect(self, client, userdata, reason_code, properties=None):  # pragma: no cover - runtime integration
        self._connected = False
        if reason_code != 0:
            self._set_last_error(f'MQTT disconnected with reason code {reason_code}')
            logger.warning('MQTT bridge disconnected with reason code %s', reason_code)

    def _on_message(self, client, userdata, message):  # pragma: no cover - runtime integration
        self.handle_message(message.topic, message.payload)

    def _set_last_error(self, message: str) -> None:
        self._last_error = message


_mqtt_bridge = MQTTBridge()


def get_mqtt_bridge() -> MQTTBridge:
    return _mqtt_bridge
