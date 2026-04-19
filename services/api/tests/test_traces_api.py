from fastapi.testclient import TestClient


def _create_reactor(client: TestClient, name: str = 'Trace Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'Trace Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def _execute(client: TestClient, **payload) -> dict:
    response = client.post('/api/v1/abrain/execute', json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_list_traces_empty_initially(client: TestClient):
    response = client.get('/api/v1/traces')
    assert response.status_code == 200
    assert response.json() == []


def test_executed_low_risk_action_records_completed_trace(client: TestClient):
    result = _execute(
        client,
        action='labos.create_task',
        params={'title': 'Trace Task', 'description': 'via trace test'},
        trace_id='trace-completed-1',
        source='abrain_adapter',
    )
    assert result['status'] == 'executed'

    traces = client.get('/api/v1/traces').json()
    assert len(traces) == 1
    trace = traces[0]
    assert trace['trace_id'] == 'trace-completed-1'
    assert trace['status'] == 'completed'
    assert trace['execution_count'] == 1
    assert trace['approval_count'] == 0

    detail = client.get('/api/v1/traces/trace-completed-1').json()
    assert detail['trace_id'] == 'trace-completed-1'
    assert len(detail['executions']) == 1
    assert detail['executions'][0]['action'] == 'labos.create_task'
    assert len(detail['approvals']) == 0
    assert len(detail['timeline']) >= 1
    exec_events = [ev for ev in detail['timeline'] if ev['kind'] == 'execution']
    assert len(exec_events) == 1
    assert exec_events[0]['status'] == 'executed'


def test_high_risk_action_creates_open_trace_with_pending_approval(client: TestClient):
    reactor_id = _create_reactor(client)
    result = _execute(
        client,
        action='labos.create_reactor_command',
        params={'reactor_id': reactor_id, 'command_type': 'light_on'},
        trace_id='trace-pending-1',
        source='abrain_adapter',
        requested_via='adapter',
        reason='pending approval trace',
    )
    assert result['status'] == 'pending_approval'

    traces = client.get('/api/v1/traces').json()
    assert any(t['trace_id'] == 'trace-pending-1' for t in traces)
    trace = next(t for t in traces if t['trace_id'] == 'trace-pending-1')
    assert trace['status'] == 'open'
    assert trace['approval_count'] == 1
    assert trace['pending_approval_count'] == 1

    detail = client.get('/api/v1/traces/trace-pending-1').json()
    assert len(detail['approvals']) == 1
    assert detail['approvals'][0]['status'] == 'pending'
    kinds = [ev['kind'] for ev in detail['timeline']]
    assert 'approval' in kinds
    assert 'execution' in kinds  # pending_approval also writes an execution log


def test_approve_flips_trace_status_to_completed(client: TestClient):
    reactor_id = _create_reactor(client)
    queued = _execute(
        client,
        action='labos.create_reactor_command',
        params={'reactor_id': reactor_id, 'command_type': 'light_on'},
        trace_id='trace-approve-flow',
        source='abrain_adapter',
        requested_via='adapter',
    )
    approval_id = queued['approval_request_id']
    assert approval_id is not None

    trace_before = client.get('/api/v1/traces/trace-approve-flow').json()
    assert trace_before['status'] == 'open'

    decision = client.post(
        f'/api/v1/approvals/{approval_id}/approve',
        json={'decision_note': 'approved in trace test'},
    )
    assert decision.status_code == 200
    assert decision.json()['status'] == 'executed'

    trace_after = client.get('/api/v1/traces/trace-approve-flow').json()
    assert trace_after['status'] == 'completed'
    assert trace_after['approval_count'] == 1
    assert trace_after['pending_approval_count'] == 0
    # at least one pending_approval execution + one executed execution
    exec_statuses = [log['status'] for log in trace_after['executions']]
    assert 'executed' in exec_statuses
    # approvals list shows final executed state
    appr_statuses = [appr['status'] for appr in trace_after['approvals']]
    assert 'executed' in appr_statuses


def test_trace_filter_by_status_and_source(client: TestClient):
    _execute(
        client,
        action='labos.create_task',
        params={'title': 'Filter Task A'},
        trace_id='trace-filter-done',
        source='abrain_adapter',
    )
    # rejected action: unknown -> trace stays open (rejected doesn't flip status)
    _execute(
        client,
        action='labos.unknown_thing',
        params={},
        trace_id='trace-filter-open',
        source='abrain_adapter',
    )

    completed = client.get('/api/v1/traces?status=completed').json()
    assert {t['trace_id'] for t in completed} == {'trace-filter-done'}

    by_source = client.get('/api/v1/traces?source=abrain').json()
    trace_ids = {t['trace_id'] for t in by_source}
    assert 'trace-filter-done' in trace_ids
    assert 'trace-filter-open' in trace_ids


def test_trace_detail_404_when_unknown(client: TestClient):
    response = client.get('/api/v1/traces/does-not-exist')
    assert response.status_code == 404


def test_abrain_adapter_query_records_trace_with_root_query(client: TestClient):
    response = client.post(
        '/api/v1/abrain/adapter/query',
        json={'question': 'Was ist jetzt wichtig?', 'dry_run': True},
    )
    assert response.status_code == 200
    payload = response.json()
    trace_id = payload['trace_id']
    assert trace_id

    detail = client.get(f'/api/v1/traces/{trace_id}').json()
    assert detail['root_query'] == 'Was ist jetzt wichtig?'
    assert detail['summary']
    assert 'open_tasks' in detail['context_snapshot']
    assert detail['status'] == 'open'
    kinds = [ev['kind'] for ev in detail['timeline']]
    assert 'query' in kinds


def test_legacy_query_response_includes_trace_id(client: TestClient):
    response = client.post(
        '/api/v1/abrain/query',
        json={'question': 'Tagesueberblick bitte', 'preset': 'daily_overview'},
    )
    assert response.status_code == 200
    trace_id = response.json().get('trace_id')
    assert trace_id
    assert client.get(f'/api/v1/traces/{trace_id}').status_code == 200
