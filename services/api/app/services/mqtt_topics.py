from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelemetryTopicMatch:
    reactor_id: int
    sensor_type: str


@dataclass(frozen=True)
class NodeTopicMatch:
    node_id: str
    message_kind: str


@dataclass(frozen=True)
class AckTopicMatch:
    reactor_id: int


def normalize_topic_prefix(prefix: str) -> list[str]:
    return [segment for segment in prefix.strip('/').split('/') if segment]


def _split_topic(topic: str) -> list[str]:
    return [segment for segment in topic.strip('/').split('/') if segment]


def parse_telemetry_topic(topic: str, *, prefix: str) -> TelemetryTopicMatch | None:
    parts = _split_topic(topic)
    prefix_parts = normalize_topic_prefix(prefix)
    if len(parts) != len(prefix_parts) + 4:
        return None
    if parts[: len(prefix_parts)] != prefix_parts:
        return None
    if parts[len(prefix_parts)] != 'reactor' or parts[len(prefix_parts) + 2] != 'telemetry':
        return None
    reactor_id_part = parts[len(prefix_parts) + 1]
    if not reactor_id_part.isdigit():
        return None
    return TelemetryTopicMatch(
        reactor_id=int(reactor_id_part),
        sensor_type=parts[len(prefix_parts) + 3],
    )


def parse_node_topic(topic: str, *, prefix: str) -> NodeTopicMatch | None:
    parts = _split_topic(topic)
    prefix_parts = normalize_topic_prefix(prefix)
    if len(parts) != len(prefix_parts) + 3:
        return None
    if parts[: len(prefix_parts)] != prefix_parts:
        return None
    if parts[len(prefix_parts)] != 'node':
        return None
    node_id = parts[len(prefix_parts) + 1]
    message_kind = parts[len(prefix_parts) + 2]
    if not node_id or message_kind not in {'status', 'heartbeat'}:
        return None
    return NodeTopicMatch(node_id=node_id, message_kind=message_kind)


def parse_ack_topic(topic: str, *, prefix: str) -> AckTopicMatch | None:
    parts = _split_topic(topic)
    prefix_parts = normalize_topic_prefix(prefix)
    if len(parts) != len(prefix_parts) + 3:
        return None
    if parts[: len(prefix_parts)] != prefix_parts:
        return None
    if parts[len(prefix_parts)] != 'reactor' or parts[len(prefix_parts) + 2] != 'ack':
        return None
    reactor_id_part = parts[len(prefix_parts) + 1]
    if not reactor_id_part.isdigit():
        return None
    return AckTopicMatch(reactor_id=int(reactor_id_part))


def build_telemetry_subscription(prefix: str) -> str:
    return '/'.join([*normalize_topic_prefix(prefix), 'reactor', '+', 'telemetry', '+'])


def build_node_subscription(prefix: str) -> str:
    return '/'.join([*normalize_topic_prefix(prefix), 'node', '+', '+'])


def build_ack_subscription(prefix: str) -> str:
    return '/'.join([*normalize_topic_prefix(prefix), 'reactor', '+', 'ack'])


def build_ack_topic(prefix: str, *, reactor_id: int) -> str:
    return '/'.join([*normalize_topic_prefix(prefix), 'reactor', str(reactor_id), 'ack'])


def get_control_channel(command_type: str) -> tuple[str, str]:
    mapping = {
        'light_on': ('light', 'on'),
        'light_off': ('light', 'off'),
        'pump_on': ('pump', 'on'),
        'pump_off': ('pump', 'off'),
        'aeration_start': ('aeration', 'start'),
        'aeration_stop': ('aeration', 'stop'),
        'sample_capture': ('sample', 'capture'),
    }
    return mapping.get(command_type, ('control', command_type))


def build_control_topic(prefix: str, *, reactor_id: int, command_type: str) -> str:
    channel, _ = get_control_channel(command_type)
    return '/'.join([*normalize_topic_prefix(prefix), 'reactor', str(reactor_id), 'control', channel])
