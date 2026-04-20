def _create_reactor(client):
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Reactor Test R1',
            'reactor_type': 'stationaer',
            'status': 'online',
            'volume_l': 1.0,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def _create_asset(client):
    response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Test Pumpe',
            'asset_type': 'pump',
            'category': 'Reactor',
            'status': 'active',
            'location': 'Lab',
        },
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def test_seeded_modules_are_listed(client):
    response = client.get('/api/v1/modules')
    assert response.status_code == 200
    data = response.json()
    ids = {module['module_id'] for module in data}
    assert 'reactor-a1' in ids
    assert 'hydro-rack-h1' in ids
    assert 'vision-v1' in ids


def test_module_overview_counts(client):
    response = client.get('/api/v1/modules/overview')
    assert response.status_code == 200
    overview = response.json()
    assert overview['total_modules'] >= 6
    assert sum(overview['by_type'].values()) == overview['total_modules']


def test_create_and_get_module(client):
    reactor_id = _create_reactor(client)

    create_response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'reactor-test-r1',
            'name': 'Reactor Test Module',
            'module_type': 'reactor',
            'status': 'nominal',
            'autonomy_level': 'assisted',
            'reactor_id': reactor_id,
            'zone': 'TestZone',
            'location': 'Rack T1',
            'description': 'Test Bioreactor Modul',
            'ros_node_name': 'labos_test_r1',
            'mqtt_node_id': 'test-r1',
            'capabilities': [
                {'capability_type': 'sense_temperature', 'is_enabled': True},
                {'capability_type': 'sense_ph', 'is_enabled': True},
            ],
        },
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created['module_id'] == 'reactor-test-r1'
    assert created['capability_count'] == 2
    assert created['reactor']['id'] == reactor_id
    assert {cap['capability_type'] for cap in created['capabilities']} == {
        'sense_temperature',
        'sense_ph',
    }

    detail_response = client.get(f"/api/v1/modules/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['module_id'] == 'reactor-test-r1'
    assert detail['reactor']['name'] == 'Reactor Test R1'
    assert detail['open_incident_count'] == 0


def test_duplicate_module_id_is_rejected(client):
    response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'reactor-a1',
            'name': 'Duplicate',
            'module_type': 'reactor',
        },
    )
    assert response.status_code == 409


def test_update_module_and_status(client):
    create_response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'vision-test',
            'name': 'Vision Test Module',
            'module_type': 'vision',
            'autonomy_level': 'autonomous',
            'capabilities': [{'capability_type': 'capture_image', 'is_enabled': True}],
        },
    )
    assert create_response.status_code == 201
    module_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/modules/{module_id}',
        json={
            'module_id': 'vision-test',
            'name': 'Vision Test Module v2',
            'module_type': 'vision',
            'status': 'attention',
            'autonomy_level': 'assisted',
            'zone': 'Grow Room',
            'description': 'Updated',
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated['name'] == 'Vision Test Module v2'
    assert updated['status'] == 'attention'
    assert updated['autonomy_level'] == 'assisted'

    status_response = client.patch(
        f'/api/v1/modules/{module_id}/status',
        json={'status': 'maintenance'},
    )
    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'maintenance'


def test_replace_capabilities(client):
    create_response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'dosing-test',
            'name': 'Dosing Test Module',
            'module_type': 'dosing',
            'capabilities': [
                {'capability_type': 'pump_fluid', 'is_enabled': True},
            ],
        },
    )
    assert create_response.status_code == 201
    module_id = create_response.json()['id']

    replace_response = client.put(
        f'/api/v1/modules/{module_id}/capabilities',
        json=[
            {'capability_type': 'pump_fluid', 'is_enabled': False},
            {'capability_type': 'dose_fluid', 'is_enabled': True},
        ],
    )
    assert replace_response.status_code == 200, replace_response.text
    capabilities = replace_response.json()
    assert {cap['capability_type'] for cap in capabilities} == {'pump_fluid', 'dose_fluid'}
    assert {cap['is_enabled'] for cap in capabilities if cap['capability_type'] == 'pump_fluid'} == {False}

    detail_response = client.get(f'/api/v1/modules/{module_id}')
    assert detail_response.status_code == 200
    assert detail_response.json()['capability_count'] == 2


def test_invalid_reactor_ref_is_rejected(client):
    response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'broken-ref',
            'name': 'Broken Ref',
            'module_type': 'reactor',
            'reactor_id': 999_999,
        },
    )
    assert response.status_code == 400


def test_filter_modules_by_type_and_status(client):
    response = client.get('/api/v1/modules?module_type=reactor')
    assert response.status_code == 200
    for module in response.json():
        assert module['module_type'] == 'reactor'

    response_nominal = client.get('/api/v1/modules?status=nominal')
    assert response_nominal.status_code == 200
    for module in response_nominal.json():
        assert module['status'] == 'nominal'


def test_modules_require_authentication(anonymous_client):
    response = anonymous_client.get('/api/v1/modules')
    assert response.status_code == 401


def test_viewer_cannot_create_module(client):
    client.post(
        '/api/v1/users',
        json={
            'username': 'modules-viewer',
            'password': 'viewer-pass-abcd',
            'display_name': 'Modules Viewer',
            'email': 'modules-viewer@local.labos',
            'role': 'viewer',
            'is_active': True,
        },
    )

    login = client.post(
        '/api/v1/auth/login',
        json={'username': 'modules-viewer', 'password': 'viewer-pass-abcd'},
    )
    assert login.status_code == 200

    response = client.post(
        '/api/v1/modules',
        json={
            'module_id': 'viewer-module',
            'name': 'Viewer Module',
            'module_type': 'utility',
        },
    )
    assert response.status_code == 403
