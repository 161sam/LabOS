from fastapi.testclient import TestClient


def _rpc(client: TestClient, method: str, params: dict | None = None, req_id: int = 1) -> dict:
    response = client.post(
        '/api/v1/mcp',
        json={
            'jsonrpc': '2.0',
            'id': req_id,
            'method': method,
            'params': params or {},
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _create_reactor(client: TestClient, name: str = 'MCP Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'MCP Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def test_initialize_returns_server_info(client: TestClient):
    body = _rpc(client, 'initialize')
    assert body['jsonrpc'] == '2.0'
    assert body['id'] == 1
    result = body['result']
    assert result['serverInfo']['name'] == 'labos-mcp'
    assert 'tools' in result['capabilities']
    assert 'resources' in result['capabilities']


def test_tools_list_matches_action_map(client: TestClient):
    body = _rpc(client, 'tools/list')
    tools = body['result']['tools']
    names = {t['name'] for t in tools}
    # Must include the canonical LabOS actions from the static ACTION_MAP.
    assert {
        'labos.create_task',
        'labos.create_alert',
        'labos.create_reactor_command',
        'labos.retry_reactor_command',
        'labos.ack_safety_incident',
    }.issubset(names)
    # Every exposed tool has a JSON Schema inputSchema + annotations.
    for tool in tools:
        assert tool['inputSchema']['type'] == 'object'
        assert 'risk_level' in tool['annotations']
        assert 'requires_approval' in tool['annotations']


def test_tools_call_executes_low_risk_action(client: TestClient):
    body = _rpc(
        client,
        'tools/call',
        {
            'name': 'labos.create_task',
            'arguments': {'title': 'MCP Task', 'description': 'via mcp test'},
            'trace_id': 'mcp-trace-1',
        },
    )
    assert 'error' not in body
    result = body['result']
    assert result['isError'] is False
    payload = result['structuredContent']
    assert payload['status'] == 'executed'
    assert payload['action'] == 'labos.create_task'
    assert payload['trace_id'] == 'mcp-trace-1'
    # Trace row created via execute_action.
    trace = client.get('/api/v1/traces/mcp-trace-1')
    assert trace.status_code == 200


def test_tools_call_high_risk_without_approve_returns_pending(client: TestClient):
    reactor_id = _create_reactor(client)
    body = _rpc(
        client,
        'tools/call',
        {
            'name': 'labos.create_reactor_command',
            'arguments': {'reactor_id': reactor_id, 'command_type': 'light_on'},
            'trace_id': 'mcp-trace-pending',
        },
    )
    payload = body['result']['structuredContent']
    assert payload['status'] == 'pending_approval'
    assert payload['approval_request_id'] is not None
    # isError flag reflects non-executed state path.
    assert body['result']['isError'] is False  # pending is not a terminal error


def test_tools_call_unknown_action_returns_rejected(client: TestClient):
    body = _rpc(
        client,
        'tools/call',
        {
            'name': 'labos.create_task',
            'arguments': {'title': 'ok'},
        },
    )
    # A known tool still works.
    assert body['result']['structuredContent']['status'] == 'executed'

    # An unregistered name is rejected at the MCP layer as NOT_FOUND.
    body2 = _rpc(
        client,
        'tools/call',
        {'name': 'labos.does_not_exist', 'arguments': {}},
    )
    assert 'error' in body2
    assert body2['error']['code'] == -32003


def test_resources_list_exposes_overview_and_reactors(client: TestClient):
    body = _rpc(client, 'resources/list')
    uris = {r['uri'] for r in body['result']['resources']}
    assert {'labos://overview', 'labos://reactors', 'labos://operations'}.issubset(uris)


def test_resources_read_returns_reactor_snapshot(client: TestClient):
    _create_reactor(client, 'MCP Reactor A')
    body = _rpc(client, 'resources/read', {'uri': 'labos://reactors'})
    contents = body['result']['contents']
    assert contents[0]['uri'] == 'labos://reactors'
    data = contents[0]['json']
    assert 'reactors' in data
    assert any(r['name'] == 'MCP Reactor A' for r in data['reactors'])


def test_resources_read_unknown_uri_returns_not_found(client: TestClient):
    body = _rpc(client, 'resources/read', {'uri': 'labos://does-not-exist'})
    assert 'error' in body
    assert body['error']['code'] == -32003


def test_unknown_method_returns_method_not_found(client: TestClient):
    body = _rpc(client, 'tools/explode')
    assert body['error']['code'] == -32601


def test_viewer_cannot_call_tools(anonymous_client: TestClient):
    # Bootstrap admin then create a viewer to test role gating at the MCP layer.
    admin_login = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'admin', 'password': 'labosadmin'},
    )
    assert admin_login.status_code == 200

    create = anonymous_client.post(
        '/api/v1/users',
        json={
            'username': 'mcpviewer',
            'password': 'viewer12345',
            'display_name': 'MCP Viewer',
            'role': 'viewer',
        },
    )
    assert create.status_code == 201, create.text

    anonymous_client.post('/api/v1/auth/logout')
    viewer_login = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'mcpviewer', 'password': 'viewer12345'},
    )
    assert viewer_login.status_code == 200

    # Viewers may read resources.
    read_resp = anonymous_client.post(
        '/api/v1/mcp',
        json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'resources/read',
            'params': {'uri': 'labos://overview'},
        },
    )
    assert read_resp.status_code == 200
    assert 'error' not in read_resp.json()

    # Viewers must NOT be able to execute tools.
    call_resp = anonymous_client.post(
        '/api/v1/mcp',
        json={
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {'name': 'labos.create_task', 'arguments': {'title': 'blocked'}},
        },
    )
    assert call_resp.status_code == 200
    assert call_resp.json()['error']['code'] == -32002


def test_invalid_jsonrpc_payload_returns_invalid_request(client: TestClient):
    response = client.post(
        '/api/v1/mcp',
        json={'method': 'tools/list'},  # missing jsonrpc field
    )
    assert response.status_code == 200
    assert response.json()['error']['code'] == -32600


def test_requires_authentication(anonymous_client: TestClient):
    response = anonymous_client.post(
        '/api/v1/mcp',
        json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'},
    )
    assert response.status_code == 401
