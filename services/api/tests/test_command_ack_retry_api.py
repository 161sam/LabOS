import json
from datetime import datetime, timedelta
from pathlib import Path

from alembic import command
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.db import get_alembic_config
from app.models import Reactor, ReactorCommand, _utcnow
from app.services import mqtt_bridge, mqtt_topics
from app.services import reactor_control as reactor_control_service


def create_reactor(client: TestClient, name: str = 'ACK Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'ACK Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


class RecordingPublisher:
    def __init__(self, result: bool | None = True):
        self.calls: list[dict] = []
        self.result = result

    def publish_reactor_command(
        self,
        *,
        reactor_id: int,
        command_id: int,
        command_type: str,
        command_uid: str | None = None,
    ) -> bool | None:
        self.calls.append(
            {
                'reactor_id': reactor_id,
                'command_id': command_id,
                'command_type': command_type,
                'command_uid': command_uid,
            }
        )
        return self.result

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def status(self):
        return None


def create_test_engine(tmp_path: Path):
    db_path = tmp_path / 'ack.db'
    database_url = f'sqlite:///{db_path}'
    command.upgrade(get_alembic_config(database_url), 'head')
    engine = create_engine(database_url, echo=False, connect_args={'check_same_thread': False})
    return engine


def seed_reactor(engine) -> int:
    with Session(engine) as session:
        reactor = Reactor(
            name='ACK Sim',
            reactor_type='tower',
            status='online',
            volume_l=1.5,
            location='ACK Lab',
        )
        session.add(reactor)
        session.commit()
        session.refresh(reactor)
        return reactor.id


def test_ack_topic_helpers():
    match = mqtt_topics.parse_ack_topic('labos/reactor/7/ack', prefix='labos')
    assert match is not None
    assert match.reactor_id == 7

    assert mqtt_topics.build_ack_topic('labos', reactor_id=3) == 'labos/reactor/3/ack'
    assert mqtt_topics.build_ack_subscription('labos') == 'labos/reactor/+/ack'
    assert mqtt_topics.parse_ack_topic('labos/reactor/abc/ack', prefix='labos') is None


def test_command_create_populates_ack_fields(tmp_path: Path):
    engine = create_test_engine(tmp_path)
    reactor_id = seed_reactor(engine)
    publisher = RecordingPublisher(result=True)

    with Session(engine) as session:
        command_read = reactor_control_service.create_reactor_command(
            session,
            reactor_id=reactor_id,
            payload=type('P', (), {'command_type': type('T', (), {'value': 'light_on'})()})(),
            publisher=publisher,
        )

    assert command_read.status == 'sent'
    assert command_read.command_uid
    assert command_read.published_at is not None
    assert command_read.timeout_at is not None
    assert command_read.retry_count == 0
    assert publisher.calls[0]['command_uid'] == command_read.command_uid


def test_ack_handler_marks_command_acknowledged(tmp_path: Path, monkeypatch):
    engine = create_test_engine(tmp_path)
    reactor_id = seed_reactor(engine)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')

    publisher = RecordingPublisher(result=True)
    with Session(engine) as session:
        command_read = reactor_control_service.create_reactor_command(
            session,
            reactor_id=reactor_id,
            payload=type('P', (), {'command_type': type('T', (), {'value': 'pump_on'})()})(),
            publisher=publisher,
        )

    bridge = mqtt_bridge.MQTTBridge(session_factory=lambda: Session(engine))
    bridge.handle_message(
        f'labos/reactor/{reactor_id}/ack',
        json.dumps(
            {
                'command_id': command_read.id,
                'command_uid': command_read.command_uid,
                'status': 'ok',
            }
        ).encode(),
    )

    with Session(engine) as session:
        stored = session.get(ReactorCommand, command_read.id)
        assert stored.status == 'acknowledged'
        assert stored.acknowledged_at is not None
        assert stored.ack_payload is not None


def test_ack_handler_error_status_marks_failed(tmp_path: Path, monkeypatch):
    engine = create_test_engine(tmp_path)
    reactor_id = seed_reactor(engine)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')

    with Session(engine) as session:
        cmd = ReactorCommand(reactor_id=reactor_id, command_type='light_on', status='sent')
        session.add(cmd)
        session.commit()
        session.refresh(cmd)
        command_uid = cmd.command_uid
        command_id = cmd.id

    bridge = mqtt_bridge.MQTTBridge(session_factory=lambda: Session(engine))
    bridge.handle_message(
        f'labos/reactor/{reactor_id}/ack',
        json.dumps(
            {
                'command_id': command_id,
                'command_uid': command_uid,
                'status': 'error',
                'error': 'relay stuck',
            }
        ).encode(),
    )

    with Session(engine) as session:
        stored = session.get(ReactorCommand, command_id)
        assert stored.status == 'failed'
        assert stored.last_error == 'relay stuck'


def test_ack_with_wrong_reactor_id_ignored(tmp_path: Path, monkeypatch):
    engine = create_test_engine(tmp_path)
    reactor_id = seed_reactor(engine)
    monkeypatch.setattr(settings, 'mqtt_topic_prefix', 'labos')

    with Session(engine) as session:
        cmd = ReactorCommand(reactor_id=reactor_id, command_type='light_on', status='sent')
        session.add(cmd)
        session.commit()
        session.refresh(cmd)
        command_id = cmd.id

    bridge = mqtt_bridge.MQTTBridge(session_factory=lambda: Session(engine))
    bridge.handle_message(
        f'labos/reactor/{reactor_id + 999}/ack',
        json.dumps({'command_id': command_id, 'status': 'ok'}).encode(),
    )

    with Session(engine) as session:
        stored = session.get(ReactorCommand, command_id)
        assert stored.status == 'sent'


def test_check_command_timeouts_transitions_sent_to_timeout(tmp_path: Path):
    engine = create_test_engine(tmp_path)
    reactor_id = seed_reactor(engine)

    with Session(engine) as session:
        stale = ReactorCommand(
            reactor_id=reactor_id,
            command_type='pump_on',
            status='sent',
            published_at=_utcnow() - timedelta(minutes=5),
            timeout_at=_utcnow() - timedelta(minutes=1),
        )
        fresh = ReactorCommand(
            reactor_id=reactor_id,
            command_type='light_on',
            status='sent',
            published_at=_utcnow(),
            timeout_at=_utcnow() + timedelta(minutes=1),
        )
        session.add_all([stale, fresh])
        session.commit()
        session.refresh(stale)
        session.refresh(fresh)
        stale_id = stale.id
        fresh_id = fresh.id

    with Session(engine) as session:
        timed_out = reactor_control_service.check_command_timeouts(session)
        assert len(timed_out) == 1
        assert timed_out[0].id == stale_id

    with Session(engine) as session:
        assert session.get(ReactorCommand, stale_id).status == 'timeout'
        assert session.get(ReactorCommand, fresh_id).status == 'sent'


def test_retry_endpoint_increments_and_republishes(client: TestClient, monkeypatch):
    reactor_id = create_reactor(client, 'Retry Reactor')
    publisher = RecordingPublisher(result=False)
    monkeypatch.setattr(
        mqtt_bridge, 'get_mqtt_bridge', lambda: publisher,
    )

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'light_on'},
    )
    assert create_response.status_code == 201
    command = create_response.json()
    assert command['status'] == 'failed'
    command_id = command['id']

    publisher.result = True
    retry_response = client.post(f'/api/v1/reactor-commands/{command_id}/retry')
    assert retry_response.status_code == 200
    retried = retry_response.json()
    assert retried['retry_count'] == 1
    assert retried['status'] == 'sent'
    assert retried['published_at'] is not None


def test_retry_rejected_when_acknowledged(client: TestClient, monkeypatch):
    reactor_id = create_reactor(client, 'Already ACK Reactor')
    publisher = RecordingPublisher(result=True)
    monkeypatch.setattr(mqtt_bridge, 'get_mqtt_bridge', lambda: publisher)

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'pump_on'},
    )
    command = create_response.json()

    ack_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'pump_off'},
    )
    ack_command = ack_response.json()

    from app.db import engine
    with Session(engine) as session:
        stored = session.get(ReactorCommand, ack_command['id'])
        stored.status = 'acknowledged'
        stored.acknowledged_at = _utcnow()
        session.add(stored)
        session.commit()

    retry_response = client.post(f'/api/v1/reactor-commands/{ack_command["id"]}/retry')
    assert retry_response.status_code == 409

    retry_first = client.post(f'/api/v1/reactor-commands/{command["id"]}/retry')
    assert retry_first.status_code == 200


def test_retry_rejected_when_max_retries_reached(client: TestClient, monkeypatch):
    reactor_id = create_reactor(client, 'Max Retry Reactor')
    publisher = RecordingPublisher(result=False)
    monkeypatch.setattr(mqtt_bridge, 'get_mqtt_bridge', lambda: publisher)

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'light_on'},
    )
    command_id = create_response.json()['id']

    from app.db import engine
    with Session(engine) as session:
        stored = session.get(ReactorCommand, command_id)
        stored.retry_count = stored.max_retries
        stored.status = 'failed'
        session.add(stored)
        session.commit()

    retry_response = client.post(f'/api/v1/reactor-commands/{command_id}/retry')
    assert retry_response.status_code == 409
    assert 'max retries' in retry_response.json()['detail'].lower()


def test_retry_requires_operator_role(client: TestClient, anonymous_client: TestClient, monkeypatch):
    reactor_id = create_reactor(client, 'RBAC Retry Reactor')
    publisher = RecordingPublisher(result=False)
    monkeypatch.setattr(mqtt_bridge, 'get_mqtt_bridge', lambda: publisher)

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'light_on'},
    )
    command_id = create_response.json()['id']

    user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'retryviewer',
            'display_name': 'Retry Viewer',
            'email': 'retryviewer@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert user_response.status_code == 201

    login_response = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'retryviewer', 'password': 'viewerpass'},
    )
    assert login_response.status_code == 200

    forbidden = anonymous_client.post(f'/api/v1/reactor-commands/{command_id}/retry')
    assert forbidden.status_code == 403
