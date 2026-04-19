from fastapi.testclient import TestClient


def _create_reactor(client: TestClient, name: str = 'Exec Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'Exec Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def _execute(client: TestClient, **payload) -> dict:
    response = client.post('/api/v1/abrain/execute', json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_list_executions_empty_initially(client: TestClient):
    response = client.get('/api/v1/abrain/executions')
    assert response.status_code == 200
    assert response.json() == []


def test_list_executions_records_executed_action(client: TestClient):
    result = _execute(
        client,
        action='labos.create_task',
        params={'title': 'Execution Task'},
        trace_id='trace-exec-1',
        source='abrain_adapter',
    )
    assert result['status'] == 'executed'

    logs = client.get('/api/v1/abrain/executions').json()
    assert len(logs) == 1
    log = logs[0]
    assert log['action'] == 'labos.create_task'
    assert log['status'] == 'executed'
    assert log['trace_id'] == 'trace-exec-1'
    assert log['approval_request_id'] is None
    assert log['blocked_reason'] is None


def test_list_executions_filter_by_status(client: TestClient):
    _execute(
        client,
        action='labos.create_task',
        params={'title': 'Filter Task'},
        trace_id='trace-exec-filter-1',
    )
    _execute(
        client,
        action='labos.unknown_action',
        params={},
        trace_id='trace-exec-filter-2',
    )

    executed = client.get('/api/v1/abrain/executions?status=executed').json()
    assert {log['action'] for log in executed} == {'labos.create_task'}

    rejected = client.get('/api/v1/abrain/executions?status=rejected').json()
    assert {log['action'] for log in rejected} == {'labos.unknown_action'}


def test_list_executions_filter_by_action_and_trace(client: TestClient):
    _execute(client, action='labos.create_task', params={'title': 'A'}, trace_id='trace-A')
    _execute(client, action='labos.create_alert', params={
        'title': 'Alert A',
        'severity': 'info',
        'source': 'abrain_adapter',
    }, trace_id='trace-B')

    by_action = client.get('/api/v1/abrain/executions?action=labos.create_task').json()
    assert all(log['action'] == 'labos.create_task' for log in by_action)

    by_trace = client.get('/api/v1/abrain/executions?trace_id=trace-B').json()
    assert len(by_trace) == 1
    assert by_trace[0]['action'] == 'labos.create_alert'


def test_list_executions_filter_by_executed_by(client: TestClient):
    _execute(
        client,
        action='labos.create_task',
        params={'title': 'Who did it'},
        trace_id='trace-who',
    )
    matching = client.get('/api/v1/abrain/executions?executed_by=admin').json()
    assert len(matching) == 1
    none_match = client.get('/api/v1/abrain/executions?executed_by=nobody').json()
    assert none_match == []


def test_pending_approval_execution_links_to_approval(client: TestClient):
    reactor_id = _create_reactor(client)
    result = _execute(
        client,
        action='labos.create_reactor_command',
        params={'reactor_id': reactor_id, 'command_type': 'light_on'},
        trace_id='trace-pending',
        source='abrain_adapter',
        requested_via='adapter',
    )
    assert result['status'] == 'pending_approval'
    approval_id = result['approval_request_id']
    assert approval_id is not None

    logs = client.get('/api/v1/abrain/executions?status=pending_approval').json()
    assert len(logs) == 1
    # The pending_approval log itself does NOT have executed_execution_log_id set on the
    # approval — that happens only after approve. So has_approval=True should exclude it,
    # and has_approval=False should include it.
    without = client.get('/api/v1/abrain/executions?has_approval=false').json()
    assert any(log['trace_id'] == 'trace-pending' for log in without)

    # Approve -> a new execution is created and linked via executed_execution_log_id.
    decision = client.post(
        f'/api/v1/approvals/{approval_id}/approve',
        json={'decision_note': 'ok'},
    )
    assert decision.status_code == 200

    by_approval = client.get(
        f'/api/v1/abrain/executions?approval_request_id={approval_id}'
    ).json()
    assert len(by_approval) == 1
    assert by_approval[0]['approval_request_id'] == approval_id
    assert by_approval[0]['status'] == 'executed'

    with_approval = client.get('/api/v1/abrain/executions?has_approval=true').json()
    assert any(log['approval_request_id'] == approval_id for log in with_approval)


def test_get_execution_detail(client: TestClient):
    result = _execute(
        client,
        action='labos.create_task',
        params={'title': 'Detail Task'},
        trace_id='trace-detail',
    )
    log_id = result['log_id']
    detail = client.get(f'/api/v1/abrain/executions/{log_id}').json()
    assert detail['id'] == log_id
    assert detail['action'] == 'labos.create_task'
    assert detail['status'] == 'executed'
    assert detail['trace_id'] == 'trace-detail'


def test_get_execution_detail_404_when_unknown(client: TestClient):
    response = client.get('/api/v1/abrain/executions/999999')
    assert response.status_code == 404


def test_executions_filter_by_unknown_approval_returns_empty(client: TestClient):
    response = client.get('/api/v1/abrain/executions?approval_request_id=999999')
    assert response.status_code == 200
    assert response.json() == []
