from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str):
    return client.post('/api/v1/auth/login', json={'username': username, 'password': password})


def create_reactor(client: TestClient, name: str = 'Telemetry Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.7,
            'location': 'Control Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def test_telemetry_ingest_and_retrieval(client: TestClient):
    reactor_id = create_reactor(client, 'Telemetry Reactor A')

    temp_response = client.post(
        '/api/v1/telemetry',
        json={
            'reactor_id': reactor_id,
            'sensor_type': 'temp',
            'value': 29.4,
            'unit': 'degC',
            'source': 'device',
            'timestamp': '2026-04-18T09:00:00',
        },
    )
    assert temp_response.status_code == 201

    ph_response = client.post(
        '/api/v1/telemetry',
        json={
            'reactor_id': reactor_id,
            'sensor_type': 'ph',
            'value': 8.7,
            'unit': 'pH',
            'source': 'manual',
            'timestamp': '2026-04-18T09:01:00',
        },
    )
    assert ph_response.status_code == 201

    temp_update_response = client.post(
        '/api/v1/telemetry',
        json={
            'reactor_id': reactor_id,
            'sensor_type': 'temp',
            'value': 30.1,
            'unit': 'degC',
            'source': 'device',
            'timestamp': '2026-04-18T09:03:00',
        },
    )
    assert temp_update_response.status_code == 201

    history_response = client.get(f'/api/v1/reactors/{reactor_id}/telemetry')
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 3
    assert history[0]['value'] == 30.1

    latest_response = client.get(f'/api/v1/reactors/{reactor_id}/telemetry/latest')
    assert latest_response.status_code == 200
    latest = latest_response.json()
    assert len(latest) == 2
    latest_temp = next(item for item in latest if item['sensor_type'] == 'temp')
    latest_ph = next(item for item in latest if item['sensor_type'] == 'ph')
    assert latest_temp['value'] == 30.1
    assert latest_ph['value'] == 8.7


def test_device_crud(client: TestClient):
    reactor_id = create_reactor(client, 'Device Reactor')

    create_response = client.post(
        '/api/v1/devices',
        json={
            'name': 'ESP32 Device Test',
            'node_id': 'esp32-device-test',
            'node_type': 'sensor_bridge',
            'status': 'online',
            'last_seen_at': '2026-04-18T08:55:00',
            'firmware_version': 'v0.1.0',
            'reactor_id': reactor_id,
        },
    )
    assert create_response.status_code == 201
    device = create_response.json()
    assert device['reactor_id'] == reactor_id
    assert device['node_id'] == 'esp32-device-test'
    assert device['node_type'] == 'sensor_bridge'

    update_response = client.patch(
        f"/api/v1/devices/{device['id']}",
        json={
            'status': 'offline',
            'last_seen_at': '2026-04-18T09:10:00',
            'firmware_version': 'v0.1.1',
            'reactor_id': reactor_id,
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['status'] == 'offline'
    assert updated['firmware_version'] == 'v0.1.1'

    list_response = client.get('/api/v1/devices')
    assert list_response.status_code == 200
    assert any(item['id'] == device['id'] for item in list_response.json())


def test_setpoint_crud(client: TestClient):
    reactor_id = create_reactor(client, 'Setpoint Reactor')

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/setpoints',
        json={
            'parameter': 'temp',
            'target_value': 31.5,
            'min_value': 30.0,
            'max_value': 33.0,
            'mode': 'auto',
        },
    )
    assert create_response.status_code == 201
    setpoint = create_response.json()
    assert setpoint['parameter'] == 'temp'
    assert setpoint['mode'] == 'auto'

    patch_response = client.patch(
        f"/api/v1/setpoints/{setpoint['id']}",
        json={
            'target_value': 32.0,
            'min_value': 30.5,
            'max_value': 33.5,
            'mode': 'manual',
        },
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched['target_value'] == 32.0
    assert patched['mode'] == 'manual'

    list_response = client.get(f'/api/v1/reactors/{reactor_id}/setpoints')
    assert list_response.status_code == 200
    assert list_response.json()[0]['target_value'] == 32.0


def test_command_creation_and_listing(client: TestClient):
    reactor_id = create_reactor(client, 'Command Reactor')

    create_response = client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'light_on'},
    )
    assert create_response.status_code == 201
    command = create_response.json()
    assert command['command_type'] == 'light_on'
    assert command['status'] == 'pending'

    list_response = client.get(f'/api/v1/reactors/{reactor_id}/commands')
    assert list_response.status_code == 200
    assert list_response.json()[0]['id'] == command['id']


def test_mqtt_status_endpoint(client: TestClient):
    response = client.get('/api/v1/reactor-control/mqtt-status')
    assert response.status_code == 200
    status = response.json()
    assert status['enabled'] is False
    assert status['connected'] is False


def test_viewer_cannot_write_reactor_control(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'controlviewer',
            'display_name': 'Control Viewer',
            'email': 'controlviewer@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201

    reactor_id = create_reactor(client, 'Viewer Control Reactor')

    login_response = login(anonymous_client, 'controlviewer', 'viewerpass')
    assert login_response.status_code == 200

    telemetry_response = anonymous_client.post(
        '/api/v1/telemetry',
        json={
            'reactor_id': reactor_id,
            'sensor_type': 'temp',
            'value': 30.0,
            'unit': 'degC',
            'source': 'manual',
        },
    )
    assert telemetry_response.status_code == 403
    assert telemetry_response.json()['detail'] == 'Operator role required'

    command_response = anonymous_client.post(
        f'/api/v1/reactors/{reactor_id}/commands',
        json={'command_type': 'pump_on'},
    )
    assert command_response.status_code == 403
    assert command_response.json()['detail'] == 'Operator role required'
