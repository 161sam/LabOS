"""Tests for ABrain V2 Reasoning Surface (/api/v1/abrain/adapter/reason)."""

from app.config import settings
from app.services import abrain_client


def _login_operator(anonymous_client):
    login_admin = anonymous_client.post(
        '/api/v1/auth/login',
        json={
            'username': settings.bootstrap_admin_username,
            'password': settings.bootstrap_admin_password,
        },
    )
    assert login_admin.status_code == 200
    create = anonymous_client.post(
        '/api/v1/users',
        json={
            'username': 'abrain-reasoning-operator',
            'password': 'reasoning-operator-pass',
            'display_name': 'Reasoning Operator',
            'email': 'reasoning-operator@local.labos',
            'role': 'operator',
            'is_active': True,
        },
    )
    assert create.status_code == 201
    anonymous_client.post('/api/v1/auth/logout')
    response = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'abrain-reasoning-operator', 'password': 'reasoning-operator-pass'},
    )
    assert response.status_code == 200


def test_reasoning_local_fallback_returns_v2_shape(client):
    response = client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'reactor_daily_overview', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['reasoning_mode'] == 'reactor_daily_overview'
    assert payload['mode'] == 'local'
    assert payload['contract_version'] == 'v1'
    assert isinstance(payload['trace_id'], str) and payload['trace_id'].startswith('labos-')
    for key in (
        'summary',
        'highlights',
        'prioritized_entities',
        'recommended_actions',
        'recommended_checks',
        'approval_required_actions',
        'blocked_or_deferred_actions',
        'used_context_sections',
    ):
        assert key in payload


def test_reasoning_mode_scopes_recommendations(client):
    incident = client.post(
        '/api/v1/safety/incidents',
        json={
            'incident_type': 'sensor_untrusted',
            'severity': 'critical',
            'title': 'Reasoning Scope Incident',
            'description': 'Incident test for reasoning scope filter.',
        },
    )
    assert incident.status_code == 201

    response = client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'incident_review', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    approval_actions = {item['action'] for item in payload['approval_required_actions']}
    assert 'labos.ack_safety_incident' in approval_actions


def test_reasoning_delegates_to_external_abrain(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')
    monkeypatch.setattr(settings, 'abrain_use_local_fallback', False)

    seen: dict[str, object] = {}

    def fake_reason(mode_value, request_payload):
        seen['mode'] = mode_value
        seen['payload'] = request_payload
        return abrain_client.ABrainClientResult(
            success=True,
            payload={
                'summary': 'ABrain V2 has spoken',
                'highlights': ['h1', 'h2'],
                'prioritized_entities': [
                    {'entity_type': 'reactor', 'entity_id': 1, 'label': 'R1', 'severity': 'warning'}
                ],
                'recommended_actions': [
                    {'action': 'labos.create_task', 'target': 'reactor:1', 'reason': 'follow up'}
                ],
                'approval_required_actions': [
                    {'action': 'labos.ack_safety_incident', 'reason': 'ack incident'}
                ],
                'blocked_or_deferred_actions': [
                    {'action': 'labos.blow_up_reactor', 'reason': 'not in catalog'}
                ],
                'recommended_checks': [
                    {'check': 'review_reactor_telemetry', 'target': 'reactor:1'}
                ],
                'used_context_sections': ['reactors', 'alerts'],
                'policy_decision': 'external_ok',
                'trace_id': 'abrain-reason-1',
            },
            mode='external',
            trace_id='abrain-reason-1',
        )

    monkeypatch.setattr(abrain_client, 'reason', fake_reason)

    response = client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'cross_domain_overview', 'question': 'Tagesstand?', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert seen['mode'] == 'cross_domain_overview'
    assert payload['mode'] == 'external'
    assert payload['trace_id'] == 'abrain-reason-1'
    assert payload['reasoning_mode'] == 'cross_domain_overview'
    recommended = {item['action'] for item in payload['recommended_actions']}
    approval = {item['action'] for item in payload['approval_required_actions']}
    blocked = {item['action'] for item in payload['blocked_or_deferred_actions']}
    assert 'labos.create_task' in recommended
    assert 'labos.ack_safety_incident' in approval
    assert 'labos.blow_up_reactor' in blocked
    assert payload['prioritized_entities'][0]['entity_type'] == 'reactor'
    assert payload['recommended_checks'][0]['check'] == 'review_reactor_telemetry'


def test_reasoning_falls_back_to_local_when_external_unreachable(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')
    monkeypatch.setattr(settings, 'abrain_use_local_fallback', True)

    monkeypatch.setattr(
        abrain_client,
        'reason',
        lambda mode_value, request_payload: abrain_client.ABrainClientResult(
            success=False, payload=None, mode='external', error='offline'
        ),
    )

    response = client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'maintenance_suggestions', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['mode'] == 'local'
    assert payload['fallback_used'] is True
    assert any('Externes ABrain nicht erreichbar' in note for note in payload['notes'])


def test_reasoning_requires_admin(anonymous_client):
    _login_operator(anonymous_client)
    response = anonymous_client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'reactor_daily_overview'},
    )
    assert response.status_code == 403


def test_reasoning_rejects_invalid_mode(client):
    response = client.post(
        '/api/v1/abrain/adapter/reason',
        json={'mode': 'unknown_mode'},
    )
    assert response.status_code == 422
