"""Invariant tests for Boundary Hardening V1.

These tests enforce the architecture boundary between LabOS and ABrain:

- Vision analysis produces only its own VisionAnalysis row — no tasks,
  alerts, or commands materialize as side effects.
- Reactor-Health assessments produce only assessments — no tasks,
  commands, or schedules are created, even under incident classification.
- Command blocking is authorized ONLY by the safety guard; every
  blocked command carries the `safety_guard:` prefix in `blocked_reason`.
- Rule executions (local-automation fallback) are tagged with
  `execution_origin='labos_local'` in their `action_result`, so
  consumers can distinguish a local side effect from ABrain-driven
  execution.
- The `signals.emit_signal` helper is a pure constructor and does not
  persist.
"""
import io

from PIL import Image
from sqlmodel import Session, select

from app import db
from app.models import (
    Photo,
    Reactor,
    ReactorCommand,
    ReactorHealthAssessment,
    ReactorTwin,
    SafetyIncident,
    Task,
    TelemetryValue,
    VisionAnalysis,
    _utcnow,
)
from app.services.signals import emit_signal


def _build_png(color=(40, 210, 70)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', (8, 8), color=color).save(buffer, format='PNG')
    return buffer.getvalue()


def _seed_reactor(session: Session, name: str) -> int:
    reactor = Reactor(
        name=name,
        reactor_type='mobil',
        status='online',
        volume_l=1.5,
        location='Lab',
    )
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    return reactor.id


def test_vision_upload_does_not_create_tasks_or_commands(client):
    with Session(db.engine) as session:
        tasks_before = len(session.exec(select(Task)).all())
        commands_before = len(session.exec(select(ReactorCommand)).all())

    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('contam.png', _build_png(color=(180, 90, 40)), 'image/png')},
    )
    assert upload.status_code == 201
    photo = upload.json()
    assert photo['latest_vision'] is not None

    with Session(db.engine) as session:
        tasks_after = len(session.exec(select(Task)).all())
        commands_after = len(session.exec(select(ReactorCommand)).all())
        analyses = session.exec(
            select(VisionAnalysis).where(VisionAnalysis.photo_id == photo['id'])
        ).all()

    assert tasks_after == tasks_before, 'vision must not create tasks'
    assert commands_after == commands_before, 'vision must not create commands'
    assert len(analyses) == 1, 'vision must produce exactly its own analysis row'


def test_reactor_health_assessment_does_not_create_commands_or_tasks(client):
    with Session(db.engine) as session:
        reactor_id = _seed_reactor(session, 'Boundary-Health')
        session.add(ReactorTwin(
            reactor_id=reactor_id,
            current_phase='growth',
            target_temp_min=20.0,
            target_temp_max=28.0,
        ))
        session.add(TelemetryValue(
            reactor_id=reactor_id,
            sensor_type='temp',
            value=33.0,
            unit='C',
            source='device',
            timestamp=_utcnow(),
        ))
        session.add(SafetyIncident(
            reactor_id=reactor_id,
            incident_type='overheating_risk',
            severity='critical',
            status='open',
            title='Boundary critical',
        ))
        session.commit()
        tasks_before = len(session.exec(select(Task)).all())
        commands_before = len(session.exec(select(ReactorCommand)).all())
        assessments_before = len(
            session.exec(select(ReactorHealthAssessment)).all()
        )

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'incident'

    with Session(db.engine) as session:
        tasks_after = len(session.exec(select(Task)).all())
        commands_after = len(session.exec(select(ReactorCommand)).all())
        assessments_after = len(
            session.exec(select(ReactorHealthAssessment)).all()
        )

    assert tasks_after == tasks_before, 'health assessment must not auto-create tasks'
    assert commands_after == commands_before, 'health assessment must not auto-create commands'
    assert assessments_after == assessments_before + 1


def test_safety_guard_is_only_command_blocker(client):
    with Session(db.engine) as session:
        reactor_id = _seed_reactor(session, 'Boundary-Safety')
        session.add(SafetyIncident(
            reactor_id=reactor_id,
            incident_type='dry_run_risk',
            severity='critical',
            status='open',
            title='Boundary dry run',
        ))
        session.commit()

    response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'pump_on'},
    )
    assert response.status_code == 201
    cmd = response.json()
    assert cmd['status'] == 'blocked'
    assert cmd['blocked_reason'] is not None
    assert cmd['blocked_reason'].startswith('safety_guard:'), (
        'boundary invariant: command blocking must be attributed to safety_guard'
    )


def test_rule_execution_tagged_as_labos_local_fallback(client):
    sensors = client.get('/api/v1/sensors').json()
    sensor = next(s for s in sensors if 'temp' in s['name'].lower() or s['name'])
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Boundary Rule Origin',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': -999.0},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Boundary origin alert {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'info',
                'source_type': 'sensor',
            },
        },
    ).json()

    response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=false")
    assert response.status_code == 200
    execution = response.json()['execution']
    assert execution['action_result']['execution_origin'] == 'labos_local', (
        'rule executions must be marked as local-automation fallback'
    )


def test_emit_signal_is_pure_constructor():
    signal = emit_signal('telemetry_out_of_range', {'reactor_id': 42, 'value': 33.0})
    assert signal == {
        'type': 'telemetry_out_of_range',
        'payload': {'reactor_id': 42, 'value': 33.0},
    }
    signal['payload']['reactor_id'] = 99
    second = emit_signal('telemetry_out_of_range', {'reactor_id': 42, 'value': 33.0})
    assert second['payload']['reactor_id'] == 42, 'emit_signal must not share payload references'


def test_emit_signal_defaults_payload_to_empty_dict():
    assert emit_signal('heartbeat') == {'type': 'heartbeat', 'payload': {}}
