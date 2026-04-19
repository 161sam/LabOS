from fastapi.testclient import TestClient

from app.config import settings


def _create_user(client: TestClient, username: str, password: str, role: str) -> int:
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
    return response.json()['id']


def _login(client: TestClient, username: str, password: str) -> None:
    response = client.post('/api/v1/auth/login', json={'username': username, 'password': password})
    assert response.status_code == 200


def _create_reactor(client: TestClient, name: str = 'Approval Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.7,
            'location': 'Approval Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def _queue_approval_via_execute(client: TestClient, reactor_id: int, trace_id: str = 'trace-appr-1') -> dict:
    response = client.post(
        '/api/v1/abrain/execute',
        json={
            'action': 'labos.create_reactor_command',
            'params': {'reactor_id': reactor_id, 'command_type': 'light_on'},
            'trace_id': trace_id,
            'source': 'abrain_adapter',
            'reason': 'Suggested by ABrain to verify lighting',
            'requested_via': 'adapter',
        },
    )
    assert response.status_code == 200
    return response.json()


def test_pending_approval_creates_approval_request_without_side_effects(client: TestClient):
    reactor_id = _create_reactor(client)
    exec_result = _queue_approval_via_execute(client, reactor_id, trace_id='trace-appr-A')
    assert exec_result['status'] == 'pending_approval'
    assert exec_result['approval_request_id'] is not None

    # No command should have been queued
    commands = client.get(f'/api/v1/reactors/{reactor_id}/commands').json()
    assert commands == []

    approvals = client.get('/api/v1/approvals').json()
    assert len(approvals) == 1
    approval = approvals[0]
    assert approval['id'] == exec_result['approval_request_id']
    assert approval['status'] == 'pending'
    assert approval['action_name'] == 'labos.create_reactor_command'
    assert approval['trace_id'] == 'trace-appr-A'
    assert approval['risk_level'] == 'high'
    assert approval['reason'] == 'Suggested by ABrain to verify lighting'
    assert approval['requested_via'] == 'adapter'
    assert approval['requested_by_source'] == 'abrain'


def test_approval_approve_triggers_execution_and_links_log(client: TestClient):
    reactor_id = _create_reactor(client)
    exec_result = _queue_approval_via_execute(client, reactor_id, trace_id='trace-appr-B')
    approval_id = exec_result['approval_request_id']

    approve_response = client.post(
        f'/api/v1/approvals/{approval_id}/approve',
        json={'decision_note': 'operator confirmed visually'},
    )
    assert approve_response.status_code == 200
    approval = approve_response.json()
    assert approval['status'] == 'executed'
    assert approval['decision_note'] == 'operator confirmed visually'
    assert approval['approved_by_username'] == settings.bootstrap_admin_username
    assert approval['executed_execution_log_id'] is not None
    assert approval['decided_at'] is not None

    # Command should now exist
    commands = client.get(f'/api/v1/reactors/{reactor_id}/commands').json()
    assert len(commands) == 1
    assert commands[0]['command_type'] == 'light_on'


def test_approval_reject_does_not_execute(client: TestClient):
    reactor_id = _create_reactor(client)
    exec_result = _queue_approval_via_execute(client, reactor_id, trace_id='trace-appr-C')
    approval_id = exec_result['approval_request_id']

    reject_response = client.post(
        f'/api/v1/approvals/{approval_id}/reject',
        json={'decision_note': 'reactor too unstable'},
    )
    assert reject_response.status_code == 200
    approval = reject_response.json()
    assert approval['status'] == 'rejected'
    assert approval['decision_note'] == 'reactor too unstable'
    assert approval['executed_execution_log_id'] is None

    commands = client.get(f'/api/v1/reactors/{reactor_id}/commands').json()
    assert commands == []


def test_approval_already_decided_cannot_be_approved_again(client: TestClient):
    reactor_id = _create_reactor(client)
    exec_result = _queue_approval_via_execute(client, reactor_id, trace_id='trace-appr-D')
    approval_id = exec_result['approval_request_id']

    first = client.post(f'/api/v1/approvals/{approval_id}/approve', json={})
    assert first.status_code == 200

    second = client.post(f'/api/v1/approvals/{approval_id}/approve', json={})
    assert second.status_code == 409


def test_approval_approve_is_still_blocked_by_safety_guard(client: TestClient):
    reactor_id = _create_reactor(client)
    exec_result = _queue_approval_via_execute(client, reactor_id, trace_id='trace-appr-E')
    approval_id = exec_result['approval_request_id']

    # Now introduce a critical safety incident that will block the command
    incident = client.post(
        '/api/v1/safety/incidents',
        json={
            'reactor_id': reactor_id,
            'incident_type': 'sensor_untrusted',
            'severity': 'critical',
            'title': 'Post-queue incident',
            'description': 'blocks command',
        },
    )
    assert incident.status_code == 201

    approve_response = client.post(f'/api/v1/approvals/{approval_id}/approve', json={})
    assert approve_response.status_code == 200
    approval = approve_response.json()
    assert approval['status'] == 'failed'
    assert approval['blocked_reason'] is not None
    assert approval['blocked_reason'].startswith('safety_guard:')


def test_approval_viewer_cannot_decide(anonymous_client: TestClient):
    _login(anonymous_client, settings.bootstrap_admin_username, settings.bootstrap_admin_password)
    reactor_id = _create_reactor(anonymous_client)
    exec_result = _queue_approval_via_execute(anonymous_client, reactor_id, trace_id='trace-appr-F')
    approval_id = exec_result['approval_request_id']

    _create_user(anonymous_client, 'appr-viewer', 'viewer-pass-abcd', 'viewer')
    anonymous_client.post('/api/v1/auth/logout')
    _login(anonymous_client, 'appr-viewer', 'viewer-pass-abcd')

    approve = anonymous_client.post(f'/api/v1/approvals/{approval_id}/approve', json={})
    assert approve.status_code == 403
    reject = anonymous_client.post(f'/api/v1/approvals/{approval_id}/reject', json={})
    assert reject.status_code == 403


def test_high_risk_approval_requires_admin(anonymous_client: TestClient):
    _login(anonymous_client, settings.bootstrap_admin_username, settings.bootstrap_admin_password)
    reactor_id = _create_reactor(anonymous_client)
    exec_result = _queue_approval_via_execute(anonymous_client, reactor_id, trace_id='trace-appr-G')
    approval_id = exec_result['approval_request_id']

    _create_user(anonymous_client, 'appr-operator', 'operator-pass-abcd', 'operator')
    anonymous_client.post('/api/v1/auth/logout')
    _login(anonymous_client, 'appr-operator', 'operator-pass-abcd')

    approve = anonymous_client.post(f'/api/v1/approvals/{approval_id}/approve', json={})
    assert approve.status_code == 403


def test_list_filter_by_status_and_trace(client: TestClient):
    reactor_id = _create_reactor(client)
    _queue_approval_via_execute(client, reactor_id, trace_id='trace-filter-1')
    _queue_approval_via_execute(client, reactor_id, trace_id='trace-filter-2')

    pending = client.get('/api/v1/approvals?status=pending').json()
    assert len(pending) == 2
    by_trace = client.get('/api/v1/approvals?trace_id=trace-filter-2').json()
    assert len(by_trace) == 1
    assert by_trace[0]['trace_id'] == 'trace-filter-2'


def test_overview_counts_are_consistent(client: TestClient):
    reactor_id = _create_reactor(client)
    _queue_approval_via_execute(client, reactor_id, trace_id='trace-ov-1')
    queued = _queue_approval_via_execute(client, reactor_id, trace_id='trace-ov-2')
    client.post(f'/api/v1/approvals/{queued["approval_request_id"]}/reject', json={})

    overview = client.get('/api/v1/approvals/overview').json()
    assert overview['pending'] == 1
    assert overview['rejected'] == 1
    assert overview['high_risk_pending'] == 1


def test_unmapped_action_does_not_create_approval_request(client: TestClient):
    response = client.post(
        '/api/v1/abrain/execute',
        json={'action': 'labos.not_a_real_action', 'params': {}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'rejected'
    assert payload['approval_request_id'] is None

    approvals = client.get('/api/v1/approvals').json()
    assert approvals == []
