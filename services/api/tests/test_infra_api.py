def _create_asset(client):
    response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Infra Test Asset',
            'asset_type': 'controller',
            'category': 'IT',
            'status': 'active',
        },
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def test_seeded_infra_nodes_are_listed(client):
    response = client.get('/api/v1/infra/nodes')
    assert response.status_code == 200
    ids = {node['node_id'] for node in response.json()}
    assert {'server-1', 'server-2', 'rtx3060-node', 'odroid-n2', 'labos-frontend'} <= ids


def test_infra_overview_counts(client):
    response = client.get('/api/v1/infra/overview')
    assert response.status_code == 200
    overview = response.json()
    assert overview['total_nodes'] >= 6
    assert sum(overview['by_type'].values()) == overview['total_nodes']
    assert sum(overview['by_role'].values()) == overview['total_nodes']
    assert overview['recent_backup_failures'] >= 1
    assert overview['degraded_services'] >= 1
    assert overview['storage_issues'] >= 1


def test_create_and_get_infra_node(client):
    create_response = client.post(
        '/api/v1/infra/nodes',
        json={
            'node_id': 'test-node-1',
            'name': 'Test Node 1',
            'node_type': 'server',
            'status': 'nominal',
            'role': 'compute',
            'hostname': 'test1.lab.local',
            'has_gpu': False,
            'mqtt_enabled': True,
        },
    )
    assert create_response.status_code == 201, create_response.text
    node_id = create_response.json()['id']

    detail_response = client.get(f'/api/v1/infra/nodes/{node_id}')
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['node_id'] == 'test-node-1'
    assert detail['services'] == []
    assert detail['storage_volumes'] == []


def test_duplicate_node_id_is_rejected(client):
    response = client.post(
        '/api/v1/infra/nodes',
        json={
            'node_id': 'server-1',
            'name': 'Duplicate',
            'node_type': 'server',
        },
    )
    assert response.status_code == 409


def test_update_node_and_status(client):
    create_response = client.post(
        '/api/v1/infra/nodes',
        json={
            'node_id': 'updatable-node',
            'name': 'Updatable Node',
            'node_type': 'gpu_node',
            'role': 'ai',
            'has_gpu': True,
        },
    )
    assert create_response.status_code == 201
    node_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/infra/nodes/{node_id}',
        json={
            'node_id': 'updatable-node',
            'name': 'Updatable Node v2',
            'node_type': 'gpu_node',
            'status': 'attention',
            'role': 'ai',
            'has_gpu': True,
            'notes': 'upgraded driver',
        },
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()['name'] == 'Updatable Node v2'
    assert update_response.json()['status'] == 'attention'

    status_response = client.patch(
        f'/api/v1/infra/nodes/{node_id}/status',
        json={'status': 'maintenance'},
    )
    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'maintenance'


def test_invalid_asset_ref_is_rejected(client):
    response = client.post(
        '/api/v1/infra/nodes',
        json={
            'node_id': 'broken-ref',
            'name': 'Broken Ref',
            'node_type': 'server',
            'asset_id': 999_999,
        },
    )
    assert response.status_code == 400


def test_filter_nodes_by_type_and_role(client):
    response = client.get('/api/v1/infra/nodes?node_type=sbc')
    assert response.status_code == 200
    for node in response.json():
        assert node['node_type'] == 'sbc'

    response = client.get('/api/v1/infra/nodes?role=ai')
    assert response.status_code == 200
    for node in response.json():
        assert node['role'] == 'ai'


def test_services_create_list_update(client):
    create_node = client.post(
        '/api/v1/infra/nodes',
        json={'node_id': 'svc-host', 'name': 'Service Host', 'node_type': 'server'},
    )
    assert create_node.status_code == 201
    node_id = create_node.json()['id']

    create_service = client.post(
        '/api/v1/infra/services',
        json={
            'infra_node_id': node_id,
            'service_name': 'redis',
            'service_type': 'database',
            'status': 'nominal',
            'port': 6379,
        },
    )
    assert create_service.status_code == 201, create_service.text
    service_id = create_service.json()['id']

    dup_response = client.post(
        '/api/v1/infra/services',
        json={
            'infra_node_id': node_id,
            'service_name': 'redis',
            'service_type': 'database',
        },
    )
    assert dup_response.status_code == 409

    list_response = client.get(f'/api/v1/infra/nodes/{node_id}/services')
    assert list_response.status_code == 200
    assert any(svc['service_name'] == 'redis' for svc in list_response.json())

    update_response = client.put(
        f'/api/v1/infra/services/{service_id}',
        json={
            'infra_node_id': node_id,
            'service_name': 'redis',
            'service_type': 'database',
            'status': 'degraded',
            'port': 6379,
            'notes': 'latency spike',
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()['status'] == 'degraded'

    filter_response = client.get('/api/v1/infra/services?status=degraded')
    assert filter_response.status_code == 200
    statuses = {svc['status'] for svc in filter_response.json()}
    assert statuses == {'degraded'}


def test_storage_and_backup_endpoints(client):
    create_node = client.post(
        '/api/v1/infra/nodes',
        json={'node_id': 'storage-host', 'name': 'Storage Host', 'node_type': 'server', 'role': 'storage'},
    )
    assert create_node.status_code == 201
    node_id = create_node.json()['id']

    volume_resp = client.post(
        '/api/v1/infra/storage',
        json={
            'infra_node_id': node_id,
            'name': 'data-vol',
            'mount_path': '/data',
            'volume_type': 'local',
            'status': 'nominal',
            'capacity_gb': 500,
            'free_gb': 250,
        },
    )
    assert volume_resp.status_code == 201, volume_resp.text

    list_volumes = client.get('/api/v1/infra/storage')
    assert list_volumes.status_code == 200
    assert any(v['name'] == 'data-vol' for v in list_volumes.json())

    backup_resp = client.post(
        '/api/v1/infra/backups',
        json={
            'infra_node_id': node_id,
            'backup_type': 'snapshot',
            'status': 'ok',
        },
    )
    assert backup_resp.status_code == 201, backup_resp.text

    list_backups = client.get('/api/v1/infra/backups?status=failed')
    assert list_backups.status_code == 200
    for record in list_backups.json():
        assert record['status'] == 'failed'


def test_infra_requires_authentication(anonymous_client):
    response = anonymous_client.get('/api/v1/infra/nodes')
    assert response.status_code == 401


def test_viewer_cannot_create_infra_node(client):
    client.post(
        '/api/v1/users',
        json={
            'username': 'infra-viewer',
            'password': 'viewer-pass-abcd',
            'display_name': 'Infra Viewer',
            'email': 'infra-viewer@local.labos',
            'role': 'viewer',
            'is_active': True,
        },
    )
    login = client.post(
        '/api/v1/auth/login',
        json={'username': 'infra-viewer', 'password': 'viewer-pass-abcd'},
    )
    assert login.status_code == 200

    response = client.post(
        '/api/v1/infra/nodes',
        json={'node_id': 'viewer-node', 'name': 'Viewer Node', 'node_type': 'server'},
    )
    assert response.status_code == 403
