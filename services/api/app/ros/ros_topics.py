"""ROS topic / service name mapping — PURE FUNCTIONS.

These helpers translate between LabOS's MQTT topic shape
(`labos/reactor/{id}/telemetry/{key}`) and ROS2's flat namespaced
form (`/reactor/{id}/{key}`). No IO here — this module is exercised
both at runtime and from unit tests without a live rclpy.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..services.mqtt_topics import (
    get_control_channel,
    normalize_topic_prefix,
    parse_telemetry_topic as parse_mqtt_telemetry_topic,
)


@dataclass(frozen=True)
class RosTelemetryMatch:
    reactor_id: int
    sensor_type: str


@dataclass(frozen=True)
class RosNodeMatch:
    node_id: str


@dataclass(frozen=True)
class RosCommandMatch:
    reactor_id: int
    command_type: str


def _split(path: str) -> list[str]:
    return [segment for segment in path.strip('/').split('/') if segment]


def build_ros_namespace(namespace: str) -> str:
    parts = _split(namespace)
    return '/' + '/'.join(parts) if parts else ''


def _ns_parts(namespace: str) -> list[str]:
    return _split(namespace)


def build_ros_telemetry_topic(namespace: str, *, reactor_id: int, sensor_type: str) -> str:
    parts = [*_ns_parts(namespace), 'reactor', str(reactor_id), sensor_type]
    return '/' + '/'.join(parts)


def parse_ros_telemetry_topic(topic: str, *, namespace: str) -> RosTelemetryMatch | None:
    parts = _split(topic)
    ns_parts = _ns_parts(namespace)
    if len(parts) != len(ns_parts) + 3:
        return None
    if parts[: len(ns_parts)] != ns_parts:
        return None
    if parts[len(ns_parts)] != 'reactor':
        return None
    reactor_id_part = parts[len(ns_parts) + 1]
    if not reactor_id_part.isdigit():
        return None
    return RosTelemetryMatch(
        reactor_id=int(reactor_id_part),
        sensor_type=parts[len(ns_parts) + 2],
    )


def build_ros_node_topic(namespace: str, *, node_id: str, kind: str = 'status') -> str:
    parts = [*_ns_parts(namespace), 'node', node_id, kind]
    return '/' + '/'.join(parts)


def build_ros_command_service(namespace: str, *, reactor_id: int, command_type: str) -> str:
    parts = [*_ns_parts(namespace), 'reactor', str(reactor_id), command_type]
    return '/' + '/'.join(parts)


def parse_ros_command_service(service: str, *, namespace: str) -> RosCommandMatch | None:
    parts = _split(service)
    ns_parts = _ns_parts(namespace)
    if len(parts) != len(ns_parts) + 3:
        return None
    if parts[: len(ns_parts)] != ns_parts:
        return None
    if parts[len(ns_parts)] != 'reactor':
        return None
    reactor_id_part = parts[len(ns_parts) + 1]
    if not reactor_id_part.isdigit():
        return None
    command_type = parts[len(ns_parts) + 2]
    # Accept any command_type; the dispatcher validates against the catalog.
    return RosCommandMatch(reactor_id=int(reactor_id_part), command_type=command_type)


def mqtt_telemetry_to_ros(
    mqtt_topic: str,
    *,
    mqtt_prefix: str,
    ros_namespace: str,
) -> str | None:
    match = parse_mqtt_telemetry_topic(mqtt_topic, prefix=mqtt_prefix)
    if match is None:
        return None
    return build_ros_telemetry_topic(
        ros_namespace,
        reactor_id=match.reactor_id,
        sensor_type=match.sensor_type,
    )


def ros_telemetry_to_mqtt(
    ros_topic: str,
    *,
    ros_namespace: str,
    mqtt_prefix: str,
) -> str | None:
    match = parse_ros_telemetry_topic(ros_topic, namespace=ros_namespace)
    if match is None:
        return None
    prefix_parts = normalize_topic_prefix(mqtt_prefix)
    parts = [*prefix_parts, 'reactor', str(match.reactor_id), 'telemetry', match.sensor_type]
    return '/'.join(parts)


def ros_service_for_command(namespace: str, command_type: str, *, reactor_id: int) -> str:
    """Convenience for outbound ROS service names; aligned with MQTT control channel labels."""
    channel, action = get_control_channel(command_type)
    parts = [*_ns_parts(namespace), 'reactor', str(reactor_id), channel, action]
    return '/' + '/'.join(parts)


__all__ = [
    'RosCommandMatch',
    'RosNodeMatch',
    'RosTelemetryMatch',
    'build_ros_command_service',
    'build_ros_namespace',
    'build_ros_node_topic',
    'build_ros_telemetry_topic',
    'mqtt_telemetry_to_ros',
    'parse_ros_command_service',
    'parse_ros_telemetry_topic',
    'ros_service_for_command',
    'ros_telemetry_to_mqtt',
]
