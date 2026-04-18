import json
from pathlib import Path

from alembic import command
from sqlmodel import Session, create_engine, select

from app.db import get_alembic_config
from app.config import settings
from app.models import DeviceNode, Reactor, TelemetryValue
from app.services import mqtt_bridge, mqtt_topics


def create_test_engine(tmp_path: Path):
    db_path = tmp_path / 'mqtt-bridge.db'
    database_url = f'sqlite:///{db_path}'
    command.upgrade(get_alembic_config(database_url), 'head')
    engine = create_engine(database_url, echo=False, connect_args={'check_same_thread': False})
    return engine


def create_reactor(engine) -> int:
    with Session(engine) as session:
        reactor = Reactor(
            name='MQTT Reactor',
            reactor_type='tower',
            status='online',
            volume_l=2.4,
            location='MQTT Bay',
        )
        session.add(reactor)
        session.commit()
        session.refresh(reactor)
        return reactor.id


def test_mqtt_topic_parsing():
    telemetry_match = mqtt_topics.parse_telemetry_topic('labos/reactor/7/telemetry/temp', prefix='labos')
    assert telemetry_match is not None
    assert telemetry_match.reactor_id == 7
    assert telemetry_match.sensor_type == 'temp'

    node_match = mqtt_topics.parse_node_topic('labos/node/esp32-a1/status', prefix='labos')
    assert node_match is not None
    assert node_match.node_id == 'esp32-a1'
    assert node_match.message_kind == 'status'

    assert mqtt_topics.build_control_topic('labos', reactor_id=3, command_type='light_on') == 'labos/reactor/3/control/light'


def test_mqtt_bridge_persists_telemetry(tmp_path: Path, monkeypatch):
    engine = create_test_engine(tmp_path)
    reactor_id = create_reactor(engine)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')
    bridge = mqtt_bridge.MQTTBridge(session_factory=lambda: Session(engine))

    bridge.handle_message(
        f'labos/reactor/{reactor_id}/telemetry/temp',
        b'{"value":29.4,"unit":"degC","source":"device"}',
    )

    with Session(engine) as session:
        telemetry = session.exec(select(TelemetryValue)).first()
        assert telemetry is not None
        assert telemetry.reactor_id == reactor_id
        assert telemetry.sensor_type == 'temp'
        assert telemetry.value == 29.4
        assert telemetry.source == 'device'

    assert bridge.status().last_message_at is not None


def test_mqtt_bridge_upserts_node_status(tmp_path: Path, monkeypatch):
    engine = create_test_engine(tmp_path)
    reactor_id = create_reactor(engine)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')
    bridge = mqtt_bridge.MQTTBridge(session_factory=lambda: Session(engine))

    payload = (
        '{"name":"ESP32 A1","reactor_id":'
        f'{reactor_id}'
        ',"node_type":"env_control","status":"warning","firmware_version":"v0.4.0"}'
    ).encode()
    bridge.handle_message(
        'labos/node/esp32-a1/status',
        payload,
    )

    with Session(engine) as session:
        device = session.exec(select(DeviceNode)).first()
        assert device is not None
        assert device.node_id == 'esp32-a1'
        assert device.reactor_id == reactor_id
        assert device.node_type == 'env_control'
        assert device.status == 'warning'
        assert device.firmware_version == 'v0.4.0'


def test_mqtt_command_publish_path(monkeypatch):
    published: dict[str, str] = {}

    class FakeMQTTModule:
        MQTT_ERR_SUCCESS = 0

    class FakePublishInfo:
        rc = 0

    class FakeClient:
        def publish(self, topic: str, payload: str, qos: int, retain: bool):
            published['topic'] = topic
            published['payload'] = payload
            published['qos'] = str(qos)
            published['retain'] = str(retain)
            return FakePublishInfo()

    monkeypatch.setattr(mqtt_bridge, 'mqtt', FakeMQTTModule())
    monkeypatch.setattr(settings, 'mqtt_enabled', True)
    monkeypatch.setattr(settings, 'mqtt_publish_commands', True)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')

    bridge = mqtt_bridge.MQTTBridge()
    bridge._client = FakeClient()
    bridge._connected = True

    assert bridge.publish_reactor_command(reactor_id=5, command_id=11, command_type='light_on') is True
    assert published['topic'] == 'labos/reactor/5/control/light'
    payload = json.loads(published['payload'])
    assert payload['command_id'] == 11
    assert payload['command'] == 'on'
    assert payload['channel'] == 'light'
