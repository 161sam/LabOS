"""ROS + MQTT Hybrid Architecture V1 — CROSS-SYSTEM ROUTING GATE.

This package defines the single coordination point between the MQTT
bridge (transport for low-power edge devices) and the ROS2 bridge
(runtime for deterministic robot workloads). Rules enforced here:

- LabOS is the only source of truth for state; ROS holds runtime
  state and MQTT is best-effort transport.
- Commands are only authorized to originate from LabOS
  (`source='labos'`); MQTT-originated commands are rejected outright.
- Telemetry and events crossing between transports must pass through
  the orchestrator so the loop-guard can prevent cycles (a message
  that arrived on MQTT is never published back to MQTT, and the same
  for ROS).
- Messages carry a `MessageEnvelope` with a `message_id` + `source`;
  duplicates (same id) are dropped.
"""
from .envelope import EnvelopeKind, MessageEnvelope, SourceTag, new_message_id
from .loop_guard import LoopGuard
from .mapping import HybridTopicMapping, build_mqtt_command_topic, build_mqtt_telemetry_topic
from .identity import NodeIdentity, IdentityRegistry, identity_from_device_node
from .orchestrator import (
    HybridOrchestrator,
    HybridPolicyError,
    HybridRouteResult,
    get_orchestrator,
)

__all__ = [
    'EnvelopeKind',
    'HybridOrchestrator',
    'HybridPolicyError',
    'HybridRouteResult',
    'HybridTopicMapping',
    'IdentityRegistry',
    'LoopGuard',
    'MessageEnvelope',
    'NodeIdentity',
    'SourceTag',
    'build_mqtt_command_topic',
    'build_mqtt_telemetry_topic',
    'get_orchestrator',
    'identity_from_device_node',
    'new_message_id',
]
