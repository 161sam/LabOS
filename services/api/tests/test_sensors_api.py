def _seed_reactor_id(client) -> int:
    response = client.get('/api/v1/reactors')
    assert response.status_code == 200
    return response.json()[0]['id']


def test_create_and_get_sensor(client):
    reactor_id = _seed_reactor_id(client)
    create_response = client.post(
        '/api/v1/sensors',
        json={
            'name': '  Mediumtemperatur B1  ',
            'sensor_type': 'water_temperature',
            'unit': ' °C ',
            'status': 'active',
            'reactor_id': reactor_id,
            'location': ' Regal B ',
            'notes': '  Testweise angelegt  ',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'Mediumtemperatur B1'
    assert created['unit'] == '°C'
    assert created['reactor_id'] == reactor_id
    assert created['location'] == 'Regal B'
    assert created['notes'] == 'Testweise angelegt'
    assert created['reactor_name']

    get_response = client.get(f"/api/v1/sensors/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_update_sensor(client):
    create_response = client.post(
        '/api/v1/sensors',
        json={
            'name': 'Raumtemperatur West',
            'sensor_type': 'temperature',
            'unit': '°C',
            'status': 'active',
            'location': 'Labor West',
        },
    )
    sensor_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/sensors/{sensor_id}',
        json={
            'name': 'Raumtemperatur West 2',
            'sensor_type': 'humidity',
            'unit': '%RH',
            'status': 'maintenance',
            'reactor_id': None,
            'location': 'Labor Nord',
            'notes': ' ',
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['name'] == 'Raumtemperatur West 2'
    assert updated['sensor_type'] == 'humidity'
    assert updated['unit'] == '%RH'
    assert updated['status'] == 'maintenance'
    assert updated['location'] == 'Labor Nord'
    assert updated['notes'] is None


def test_change_sensor_status(client):
    create_response = client.post(
        '/api/v1/sensors',
        json={
            'name': 'EC Sonde B1',
            'sensor_type': 'ec',
            'unit': 'mS/cm',
            'status': 'active',
        },
    )
    sensor_id = create_response.json()['id']

    status_response = client.patch(
        f'/api/v1/sensors/{sensor_id}/status',
        json={'status': 'error'},
    )

    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'error'


def test_create_sensor_value_and_list_values(client):
    create_response = client.post(
        '/api/v1/sensors',
        json={
            'name': 'pH Sonde B2',
            'sensor_type': 'ph',
            'unit': 'pH',
            'status': 'active',
        },
    )
    sensor_id = create_response.json()['id']

    first_value = client.post(
        f'/api/v1/sensors/{sensor_id}/values',
        json={
            'value': 7.2,
            'recorded_at': '2026-04-17T10:00:00',
            'source': 'manual',
        },
    )
    assert first_value.status_code == 201

    second_value = client.post(
        f'/api/v1/sensors/{sensor_id}/values',
        json={
            'value': 7.0,
            'recorded_at': '2026-04-17T10:15:00',
            'source': 'import',
        },
    )
    assert second_value.status_code == 201

    latest_response = client.get(f'/api/v1/sensors/{sensor_id}/values', params={'limit': 1})
    assert latest_response.status_code == 200
    latest_values = latest_response.json()
    assert len(latest_values) == 1
    assert latest_values[0]['value'] == 7.0
    assert latest_values[0]['source'] == 'import'

    filtered_response = client.get(
        f'/api/v1/sensors/{sensor_id}/values',
        params={'from': '2026-04-17T10:05:00', 'to': '2026-04-17T10:20:00'},
    )
    assert filtered_response.status_code == 200
    filtered_values = filtered_response.json()
    assert len(filtered_values) == 1
    assert filtered_values[0]['value'] == 7.0

    sensor_list_response = client.get('/api/v1/sensors')
    assert sensor_list_response.status_code == 200
    created_sensor = next(sensor for sensor in sensor_list_response.json() if sensor['id'] == sensor_id)
    assert created_sensor['last_value'] == 7.0
    assert created_sensor['last_value_source'] == 'import'


def test_sensor_overview_returns_latest_values(client):
    response = client.get('/api/v1/sensors/overview', params={'limit': 2})
    assert response.status_code == 200
    overview = response.json()
    assert len(overview) == 2
    assert 'status' in overview[0]
    assert 'last_value' in overview[0]


def test_create_sensor_rejects_missing_reactor(client):
    response = client.post(
        '/api/v1/sensors',
        json={
            'name': 'Licht West',
            'sensor_type': 'light',
            'unit': 'lux',
            'status': 'active',
            'reactor_id': 99999,
        },
    )

    assert response.status_code == 422
    assert response.json()['detail'] == 'Referenced reactor does not exist'


def test_create_sensor_value_rejects_unknown_sensor(client):
    response = client.post(
        '/api/v1/sensors/99999/values',
        json={'value': 25.0},
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'Sensor not found'
