from fastapi.testclient import TestClient

from app.config import settings
from app.services import abrain_execution


def _login_as(client: TestClient, username: str, password: str):
    return client.post('/api/v1/auth/login', json={'username': username, 'password': password})


def _create_user(client: TestClient, username: str, password: str, role: str) -> None:
    response = client.post(
        '/api/v1/users',
        json={
            'username': username,
            'password': password,
            'display_name': username,
            'email': f'{username}@local.labos',
            'role': role,
            'is_active': True,
        },
    )
    assert response.status_code == 201


def _create_reactor(client: TestClient, name: str = 'Execute Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.7,
            'location': 'Exec Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def test_action_map_is_static_and_covers_core_actions():
    expected = {
        'labos.create_task',
        'labos.create_alert',
        'labos.create_reactor_command',
        'labos.retry_reactor_command',
        'labos.ack_safety_incident',
    }
    assert expected <= set(abrain_execution.ACTION_MAP.keys())


def test_execute_low_risk_action_is_logged_as_executed(client: TestClient):
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_task',
            'params': {'title': 'ABrain Task', 'description': 'from adapter'},
            'trace_id': 'trace-exec-1',
            'source': 'abrain_adapter',
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'executed'
    assert payload['action'] == 'labos.create_task'
    assert payload['blocked_reason'] is None
    assert payload['trace_id'] == 'trace-exec-1'
    assert payload['log_id'] is not None
    assert payload['result']['title'] == 'ABrain Task'


def test_execute_unmapped_action_is_rejected_not_executed(client: TestClient):
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.blow_up_reactor',
            'params': {},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'rejected'
    assert payload['blocked_reason'] == 'action_not_in_catalog'
    assert payload['log_id'] is not None


def test_execute_action_outside_catalog_is_not_in_action_map():
    # Guard the static invariant: ACTION_MAP has no entry for non-catalog keys
    from app.services import abrain_actions

    catalog_names = {d.name for d in abrain_actions.get_catalog().actions}
    for mapped_name in abrain_execution.ACTION_MAP:
        assert mapped_name in catalog_names


def test_execute_requires_approval_for_high_risk_action(client: TestClient):
    reactor_id = _create_reactor(client)
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_reactor_command',
            'params': {'reactor_id': reactor_id, 'command_type': 'light_on'},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'pending_approval'
    assert payload['blocked_reason'] == 'approval_required'
    assert payload['requires_approval'] is True
    # Verify no command was actually queued
    list_response = client.get(f'/api/v1/reactors/{reactor_id}/commands')
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_execute_high_risk_action_runs_when_approved(client: TestClient):
    reactor_id = _create_reactor(client)
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_reactor_command',
            'params': {'reactor_id': reactor_id, 'command_type': 'light_on'},
            'approve': True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'executed'
    assert payload['result']['reactor_id'] == reactor_id
    assert payload['result']['command_type'] == 'light_on'


def test_execute_reactor_command_is_blocked_by_safety_guard(client: TestClient):
    reactor_id = _create_reactor(client)
    incident = client.post(
        '/api/v1/safety/incidents',
        json={
            'reactor_id': reactor_id,
            'incident_type': 'sensor_untrusted',
            'severity': 'critical',
            'title': 'Guard-Test Incident',
            'description': 'blocks commands',
        },
    )
    assert incident.status_code == 201

    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_reactor_command',
            'params': {'reactor_id': reactor_id, 'command_type': 'pump_on'},
            'approve': True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'blocked'
    assert payload['blocked_reason'] is not None
    assert payload['blocked_reason'].startswith('safety_guard:')


def test_execute_role_check_rejects_viewer(anonymous_client: TestClient):
    login_admin = anonymous_client.post(
        '/api/v1/auth/login',
        json={
            'username': settings.bootstrap_admin_username,
            'password': settings.bootstrap_admin_password,
        },
    )
    assert login_admin.status_code == 200
    _create_user(anonymous_client, 'abrain-viewer', 'viewer-pass-1234', 'viewer')
    anonymous_client.post('/api/v1/auth/logout')

    login = _login_as(anonymous_client, 'abrain-viewer', 'viewer-pass-1234')
    assert login.status_code == 200

    response = anonymous_client.post(
        '/api/v1/abrain/execute',
        json={'action': 'labos.create_task', 'params': {'title': 'Viewer attempt'}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'rejected'
    assert payload['blocked_reason'].startswith('role_not_allowed')


def test_execute_writes_execution_log_with_trace_id(client: TestClient):
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_alert',
            'params': {
                'title': 'Logged alert',
                'message': 'Test message',
                'severity': 'warning',
                'source_type': 'manual',
            },
            'trace_id': 'trace-log-42',
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'executed'
    assert payload['trace_id'] == 'trace-log-42'
    assert payload['executed_by'] == settings.bootstrap_admin_username
    assert payload['log_id'] is not None
