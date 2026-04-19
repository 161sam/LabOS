from app.config import settings
from app.services import abrain_actions, abrain_client


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
            'username': 'abrain-operator',
            'password': 'operator-abrain-pass',
            'display_name': 'ABrain Operator',
            'email': 'abrain-operator@local.labos',
            'role': 'operator',
            'is_active': True,
        },
    )
    assert create.status_code == 201
    anonymous_client.post('/api/v1/auth/logout')
    response = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'abrain-operator', 'password': 'operator-abrain-pass'},
    )
    assert response.status_code == 200


def test_abrain_actions_catalog_returns_static_surface(client):
    response = client.get('/api/v1/abrain/actions')

    assert response.status_code == 200
    payload = response.json()
    assert payload['contract_version'] == 'v1'
    names = {action['name'] for action in payload['actions']}
    assert {
        'labos.create_task',
        'labos.create_alert',
        'labos.run_reactor_health_assessment',
        'labos.create_reactor_command',
        'labos.retry_reactor_command',
        'labos.ack_safety_incident',
        'labos.create_maintenance_record',
        'labos.create_calibration_record',
        'labos.run_schedule_now',
    } <= names


def test_abrain_adapter_context_returns_structured_sections(client):
    response = client.get('/api/v1/abrain/adapter/context')

    assert response.status_code == 200
    payload = response.json()
    assert payload['contract_version'] == 'v1'
    assert payload['mode'] in {'local', 'auto', 'external'}
    assert payload['fallback_used'] is False
    assert 'reactors' in payload and isinstance(payload['reactors'], list)
    assert 'operations' in payload
    assert 'resources' in payload
    assert 'schedule' in payload
    summary = payload['summary']
    assert {'open_tasks', 'critical_alerts', 'reactors_online'} <= set(summary.keys())
    operations = payload['operations']
    assert {
        'overdue_tasks',
        'critical_alerts',
        'blocked_command_count',
        'failed_command_count',
        'due_calibration_count',
        'overdue_maintenance_count',
        'open_safety_incident_count',
    } <= set(operations.keys())


def test_abrain_adapter_query_returns_local_response_in_stub_mode(client):
    response = client.post(
        '/api/v1/abrain/adapter/query',
        json={
            'question': 'Was sollte ich jetzt anschauen?',
            'preset': 'critical_issues',
            'dry_run': True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['mode'] == 'local'
    assert payload['contract_version'] == 'v1'
    assert payload['fallback_used'] is False
    assert payload['policy_decision'] == 'local_rules_v1'
    assert isinstance(payload['trace_id'], str) and payload['trace_id'].startswith('labos-')
    assert isinstance(payload['recommended_actions'], list)
    assert isinstance(payload['blocked_actions'], list)
    assert isinstance(payload['highlights'], list)


def test_abrain_adapter_query_recommends_catalog_actions_on_safety_signal(client):
    incident_payload = {
        'incident_type': 'sensor_untrusted',
        'severity': 'critical',
        'title': 'Sensor Ausfall',
        'description': 'Test-Incident fuer Adapter-Recommendations',
    }
    created = client.post('/api/v1/safety/incidents', json=incident_payload)
    assert created.status_code == 201

    response = client.post(
        '/api/v1/abrain/adapter/query',
        json={'question': 'Status kritischer Themen?', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    action_names = {item['action'] for item in payload['recommended_actions']}
    assert 'labos.ack_safety_incident' in action_names
    ack_item = next(item for item in payload['recommended_actions'] if item['action'] == 'labos.ack_safety_incident')
    assert ack_item['requires_approval'] is True
    assert payload['approval_required'] is True


def test_abrain_adapter_query_blocks_unknown_external_actions(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')
    monkeypatch.setattr(settings, 'abrain_use_local_fallback', False)

    from app.services import abrain_client as client_module

    def fake_query(request_payload):
        return client_module.ABrainClientResult(
            success=True,
            payload={
                'summary': 'external decision',
                'highlights': ['h1'],
                'recommended_actions': [
                    {'action': 'labos.create_task', 'target': 'alert:1', 'reason': 'catalog action'},
                    {'action': 'labos.blow_up_reactor', 'reason': 'not in catalog'},
                ],
                'policy_decision': 'external_ok',
                'trace_id': 'abrain-123',
            },
            mode='external',
            trace_id='abrain-123',
        )

    monkeypatch.setattr(abrain_client, 'query', fake_query)

    response = client.post(
        '/api/v1/abrain/adapter/query',
        json={'question': 'Bitte extern entscheiden', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['mode'] == 'external'
    assert payload['fallback_used'] is False
    assert payload['trace_id'] == 'abrain-123'
    recommended = {item['action'] for item in payload['recommended_actions']}
    blocked = {item['action'] for item in payload['blocked_actions']}
    assert 'labos.create_task' in recommended
    assert 'labos.blow_up_reactor' in blocked
    blow_up = next(item for item in payload['blocked_actions'] if item['action'] == 'labos.blow_up_reactor')
    assert blow_up['blocked'] is True
    assert blow_up['blocked_reason'] == 'action_not_in_catalog'


def test_abrain_adapter_query_falls_back_to_local_when_external_unreachable(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')
    monkeypatch.setattr(settings, 'abrain_use_local_fallback', True)

    from app.services import abrain_client as client_module

    monkeypatch.setattr(
        abrain_client,
        'query',
        lambda request_payload: client_module.ABrainClientResult(
            success=False, payload=None, mode='external', error='offline'
        ),
    )

    response = client.post(
        '/api/v1/abrain/adapter/query',
        json={'question': 'Fallback bitte', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['mode'] == 'local'
    assert payload['fallback_used'] is True
    assert 'Externes ABrain nicht erreichbar' in ' '.join(payload['notes'])


def test_abrain_adapter_query_requires_admin_role(anonymous_client):
    _login_operator(anonymous_client)
    response = anonymous_client.post(
        '/api/v1/abrain/adapter/query',
        json={'question': 'Darf ich?', 'dry_run': True},
    )
    assert response.status_code == 403


def test_abrain_action_catalog_consistency_with_service_module():
    catalog = abrain_actions.get_catalog()
    # Each action resolves via find_action
    for descriptor in catalog.actions:
        assert abrain_actions.find_action(descriptor.name) is descriptor
    # High-risk actions require approval
    for descriptor in catalog.actions:
        if descriptor.risk_level.value in {'high', 'critical'}:
            assert descriptor.requires_approval is True
