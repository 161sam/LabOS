from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import db as db_module
from app.config import settings
from app.models import DeviceNode, UserAccount
from app.ros import (
    RosBridge,
    build_ros_command_service,
    build_ros_namespace,
    build_ros_node_name,
    build_ros_telemetry_topic,
    dispatch_ros_command,
    list_ros_nodes,
    mqtt_telemetry_to_ros,
    parse_ros_command_service,
    parse_ros_telemetry_topic,
    resolve_command_type_from_ros,
    resolve_device_node_by_ros_name,
    ros_telemetry_to_mqtt,
)
from app.ros.ros_actions import ROS_REQUESTED_VIA, ROS_SOURCE
from app.ros.ros_bridge import get_ros_bridge
from app.schemas import ApprovalRequestVia, UserRead
from app.services import users as users_service


def _create_reactor(client: TestClient, name: str = 'ROS Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 3.0,
            'location': 'ROS Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def _admin_user() -> UserRead:
    with Session(db_module.engine) as session:
        user = session.exec(
            select(UserAccount).where(
                UserAccount.username == settings.bootstrap_admin_username
            )
        ).one()
        return users_service._to_user_read(user)


def test_topic_roundtrip_ros_and_mqtt():
    ros_topic = build_ros_telemetry_topic('/labos', reactor_id=7, sensor_type='ph')
    assert ros_topic == '/labos/reactor/7/ph'
    match = parse_ros_telemetry_topic(ros_topic, namespace='/labos')
    assert match is not None
    assert match.reactor_id == 7
    assert match.sensor_type == 'ph'

    mqtt_topic = ros_telemetry_to_mqtt(ros_topic, ros_namespace='/labos', mqtt_prefix='labos')
    assert mqtt_topic == 'labos/reactor/7/telemetry/ph'

    back = mqtt_telemetry_to_ros(mqtt_topic, mqtt_prefix='labos', ros_namespace='/labos')
    assert back == ros_topic


def test_parse_ros_telemetry_topic_rejects_malformed():
    assert parse_ros_telemetry_topic('/labos/reactor/abc/ph', namespace='/labos') is None
    assert parse_ros_telemetry_topic('/labos/foo/1/ph', namespace='/labos') is None
    assert parse_ros_telemetry_topic('/other/reactor/1/ph', namespace='/labos') is None


def test_parse_ros_command_service_roundtrip():
    service = build_ros_command_service('/labos', reactor_id=3, command_type='light_on')
    assert service == '/labos/reactor/3/light_on'
    match = parse_ros_command_service(service, namespace='/labos')
    assert match is not None
    assert match.reactor_id == 3
    assert match.command_type == 'light_on'


def test_build_ros_namespace_normalizes():
    assert build_ros_namespace('labos') == '/labos'
    assert build_ros_namespace('/labos/') == '/labos'
    assert build_ros_namespace('/labos/sub') == '/labos/sub'


def test_resolve_command_type_whitelist():
    assert resolve_command_type_from_ros('light_on') == 'light_on'
    assert resolve_command_type_from_ros('blow_up_reactor') is None


def test_registry_builds_ros_node_name():
    device = DeviceNode(id=42, name='ESP Alpha', node_id='esp-alpha-01', node_type='esp32')
    assert build_ros_node_name(device) == 'labos_node_42_esp_alpha_01'


def test_list_ros_nodes_and_resolve(client: TestClient):
    reactor_id = _create_reactor(client, 'ROS Node Reactor')
    create = client.post(
        '/api/v1/devices',
        json={
            'name': 'ESP Node X',
            'node_id': 'esp-node-x',
            'node_type': 'sensor_bridge',
            'status': 'online',
            'reactor_id': reactor_id,
        },
    )
    assert create.status_code == 201, create.text

    with Session(db_module.engine) as session:
        entries = list_ros_nodes(session)
        target = next((entry for entry in entries if entry.node_id == 'esp-node-x'), None)
        assert target is not None
        assert target.ros_node_name.startswith('labos_node_')

        resolved = resolve_device_node_by_ros_name(session, target.ros_node_name)
        assert resolved is not None
        assert resolved.node_id == 'esp-node-x'

        assert resolve_device_node_by_ros_name(session, 'some_other_node_999') is None


def test_dispatch_ros_command_high_risk_requires_approval(client: TestClient):
    reactor_id = _create_reactor(client, 'ROS High Risk')
    user = _admin_user()
    with Session(db_module.engine) as session:
        outcome = dispatch_ros_command(
            session,
            user,
            reactor_id=reactor_id,
            command_type='light_on',
            trace_id='ros-trace-high',
        )
    assert outcome.accepted is True
    assert outcome.result is not None
    # High-risk reactor commands require approval — ROS must honor the gate.
    assert outcome.result.status.value == 'pending_approval'
    assert outcome.result.approval_request_id is not None
    assert outcome.result.source == ROS_SOURCE

    approval_id = outcome.result.approval_request_id
    detail = client.get(f'/api/v1/approvals/{approval_id}')
    assert detail.status_code == 200
    assert detail.json()['requested_via'] == ApprovalRequestVia.ros.value


def test_dispatch_ros_command_rejects_unknown_command_type(client: TestClient):
    reactor_id = _create_reactor(client, 'ROS Unknown Cmd')
    user = _admin_user()
    with Session(db_module.engine) as session:
        outcome = dispatch_ros_command(
            session,
            user,
            reactor_id=reactor_id,
            command_type='launch_missiles',
        )
    assert outcome.accepted is False
    assert outcome.rejection_reason is not None
    assert outcome.rejection_reason.startswith('unknown_ros_command_type')
    assert outcome.result is None


def test_bridge_reports_status_when_dependency_missing(monkeypatch):
    from app.ros import ros_bridge as bridge_mod

    monkeypatch.setattr(bridge_mod, 'rclpy', None)
    bridge = RosBridge()
    status = bridge.status()
    assert status.dependency_available is False
    assert status.running is False
    monkeypatch.setattr(settings, 'ros_enabled', True)
    bridge.start()
    assert bridge.status().running is False
    assert (bridge.status().last_error or '').startswith('rclpy dependency not installed')


def test_bridge_stays_dormant_when_disabled():
    bridge = get_ros_bridge()
    bridge.start()
    status = bridge.status()
    assert status.enabled is False
    assert status.running is False


def test_requested_via_enum_includes_ros():
    assert ApprovalRequestVia.ros.value == 'ros'
    assert ROS_REQUESTED_VIA == 'ros'
