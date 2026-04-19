import pytest

from app.ros_mqtt_hybrid import (
    EnvelopeKind,
    HybridOrchestrator,
    HybridPolicyError,
    LoopGuard,
    MessageEnvelope,
    SourceTag,
    build_mqtt_command_topic,
    build_mqtt_telemetry_topic,
    get_orchestrator,
    new_message_id,
)
from app.ros_mqtt_hybrid.identity import (
    NodeIdentity,
    identity_from_device_node,
)
from app.ros_mqtt_hybrid.mapping import HybridTopicMapping, default_mapping
from app.models import DeviceNode


def _make_orchestrator() -> tuple[HybridOrchestrator, list[MessageEnvelope], list[MessageEnvelope]]:
    orch = HybridOrchestrator()
    mqtt_calls: list[MessageEnvelope] = []
    ros_calls: list[MessageEnvelope] = []
    orch.register_mqtt_publisher(lambda env: mqtt_calls.append(env))
    orch.register_ros_publisher(lambda env: ros_calls.append(env))
    return orch, mqtt_calls, ros_calls


def test_mqtt_telemetry_forwards_to_ros_only():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.mqtt,
        kind=EnvelopeKind.telemetry,
        reactor_id=1,
        key='temp',
        value=24.5,
        unit='c',
    )
    result = orch.publish_telemetry(env)
    assert result.accepted is True
    assert result.forwarded_to_ros is True
    assert result.forwarded_to_mqtt is False
    assert len(ros_calls) == 1
    assert ros_calls[0].reactor_id == 1
    assert ros_calls[0].key == 'temp'
    assert len(mqtt_calls) == 0


def test_ros_telemetry_forwards_to_mqtt_only():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.ros,
        kind=EnvelopeKind.telemetry,
        reactor_id=2,
        key='ph',
        value=7.1,
        unit='ph',
    )
    result = orch.publish_telemetry(env)
    assert result.accepted is True
    assert result.forwarded_to_mqtt is True
    assert result.forwarded_to_ros is False
    assert len(mqtt_calls) == 1
    assert len(ros_calls) == 0


def test_loop_prevention_never_echoes_back_to_source():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.mqtt,
        kind=EnvelopeKind.telemetry,
        reactor_id=7,
        key='temp',
        value=21.0,
    )
    orch.publish_telemetry(env)
    for call in mqtt_calls:
        assert call.source != SourceTag.mqtt  # Never reached; the list stays empty
    assert mqtt_calls == []


def test_duplicate_messages_are_dropped():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    message_id = new_message_id()
    env1 = MessageEnvelope(
        message_id=message_id,
        source=SourceTag.mqtt,
        kind=EnvelopeKind.telemetry,
        reactor_id=3,
        key='temp',
        value=22.1,
    )
    env2 = MessageEnvelope(
        message_id=message_id,
        source=SourceTag.mqtt,
        kind=EnvelopeKind.telemetry,
        reactor_id=3,
        key='temp',
        value=22.1,
    )
    first = orch.publish_telemetry(env1)
    second = orch.publish_telemetry(env2)
    assert first.accepted is True
    assert second.accepted is False
    assert second.dropped_reason == 'duplicate_message_id'
    assert len(ros_calls) == 1


def test_mqtt_originated_command_is_rejected():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.mqtt,
        kind=EnvelopeKind.command,
        reactor_id=4,
        key='light_on',
    )
    with pytest.raises(HybridPolicyError):
        orch.publish_command(env)
    assert mqtt_calls == []
    assert ros_calls == []
    assert orch.stats().rejected_commands == 1


def test_ros_originated_command_is_also_rejected():
    orch, _, _ = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.ros,
        kind=EnvelopeKind.command,
        reactor_id=4,
        key='pump_on',
    )
    with pytest.raises(HybridPolicyError):
        orch.publish_command(env)


def test_labos_command_fans_out_to_both_transports():
    orch, mqtt_calls, ros_calls = _make_orchestrator()
    env = MessageEnvelope(
        source=SourceTag.labos,
        kind=EnvelopeKind.command,
        reactor_id=5,
        key='light_on',
        extras={'command_id': 42},
    )
    result = orch.publish_command(env)
    assert result.accepted is True
    assert result.forwarded_to_mqtt is True
    assert result.forwarded_to_ros is True
    assert len(mqtt_calls) == 1
    assert len(ros_calls) == 1
    assert mqtt_calls[0].extras['command_id'] == 42


def test_publish_wrong_kind_to_wrong_method_raises():
    orch = HybridOrchestrator()
    env = MessageEnvelope(
        source=SourceTag.labos,
        kind=EnvelopeKind.telemetry,
        reactor_id=1,
        key='temp',
        value=1.0,
    )
    with pytest.raises(HybridPolicyError):
        orch.publish_command(env)
    env2 = MessageEnvelope(
        source=SourceTag.labos,
        kind=EnvelopeKind.command,
        reactor_id=1,
        key='light_on',
    )
    with pytest.raises(HybridPolicyError):
        orch.publish_telemetry(env2)


def test_loop_guard_sliding_window():
    guard = LoopGuard(max_size=3)
    assert guard.admit('a') is True
    assert guard.admit('b') is True
    assert guard.admit('c') is True
    # seeing 'a' again refreshes its position (order: b, c, a)
    assert guard.admit('a') is False
    # now admitting 'd' evicts the oldest, which is 'b'
    assert guard.admit('d') is True
    # 'c' and 'a' remain, so they are still flagged as duplicates
    assert guard.admit('c') is False
    assert guard.admit('a') is False
    # 'b' was evicted, so it's admissible again
    assert guard.admit('b') is True


def test_mapping_produces_canonical_topics():
    mapping = HybridTopicMapping(mqtt_prefix='labos', ros_namespace='/labos')
    assert mapping.mqtt_telemetry_topic(reactor_id=1, sensor_type='temp') == 'labos/reactor/1/telemetry/temp'
    assert mapping.ros_telemetry_topic(reactor_id=1, sensor_type='temp') == '/labos/reactor/1/temp'
    assert mapping.mqtt_command_topic(reactor_id=3, command_type='light_on') == 'labos/reactor/3/control/light'
    assert mapping.ros_command_service(reactor_id=3, command_type='light_on') == '/labos/reactor/3/light_on'


def test_mapping_cross_translates_telemetry():
    mapping = HybridTopicMapping(mqtt_prefix='labos', ros_namespace='/labos')
    assert mapping.mqtt_to_ros_telemetry('labos/reactor/9/telemetry/ph') == '/labos/reactor/9/ph'
    assert mapping.ros_to_mqtt_telemetry('/labos/reactor/9/ph') == 'labos/reactor/9/telemetry/ph'


def test_default_mapping_matches_settings():
    mapping = default_mapping()
    assert mapping.mqtt_prefix == 'labos'
    assert mapping.ros_namespace == '/labos'
    assert build_mqtt_telemetry_topic(2, 'temp') == 'labos/reactor/2/telemetry/temp'
    assert build_mqtt_command_topic(2, 'light_on') == 'labos/reactor/2/control/light'


def test_identity_from_device_node():
    device = DeviceNode(
        id=7,
        name='env-1',
        node_id='env-1',
        node_type='env_control',
        reactor_id=1,
    )
    identity = identity_from_device_node(device)
    assert isinstance(identity, NodeIdentity)
    assert identity.node_id == 'env-1'
    assert identity.mqtt_client_id == 'env-1'
    assert identity.ros_node.startswith('labos_node_7_')
    assert identity.reactor_id == 1
    assert identity.type == 'env_control'


def test_module_level_orchestrator_is_singleton():
    a = get_orchestrator()
    b = get_orchestrator()
    assert a is b
