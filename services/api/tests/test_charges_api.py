def _seed_reactor_id(client) -> int:
    response = client.get('/api/v1/reactors')
    assert response.status_code == 200
    return response.json()[0]['id']


def test_create_and_get_charge(client):
    reactor_id = _seed_reactor_id(client)
    create_response = client.post(
        '/api/v1/charges',
        json={
            'name': '  Charge-010  ',
            'species': ' Chlorella sorokiniana ',
            'status': 'planned',
            'reactor_id': reactor_id,
            'start_date': '2026-04-17',
            'volume_l': 2.5,
            'notes': '  Start vorbereitet  ',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'Charge-010'
    assert created['species'] == 'Chlorella sorokiniana'
    assert created['status'] == 'planned'
    assert created['reactor_id'] == reactor_id
    assert created['notes'] == 'Start vorbereitet'

    get_response = client.get(f"/api/v1/charges/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_update_charge(client):
    reactor_id = _seed_reactor_id(client)
    create_response = client.post(
        '/api/v1/charges',
        json={
            'name': 'Charge-011',
            'species': 'Spirulina',
            'status': 'planned',
            'reactor_id': reactor_id,
            'start_date': '2026-04-17',
            'volume_l': 1.1,
            'notes': 'Initial',
        },
    )
    charge_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/charges/{charge_id}',
        json={
            'name': 'Charge-011B',
            'species': 'Spirulina maxima',
            'status': 'active',
            'reactor_id': None,
            'start_date': '2026-04-18',
            'volume_l': 1.4,
            'notes': '  ',
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['name'] == 'Charge-011B'
    assert updated['species'] == 'Spirulina maxima'
    assert updated['status'] == 'active'
    assert updated['reactor_id'] is None
    assert updated['start_date'] == '2026-04-18'
    assert updated['notes'] is None


def test_change_charge_status(client):
    reactor_id = _seed_reactor_id(client)
    create_response = client.post(
        '/api/v1/charges',
        json={
            'name': 'Charge-012',
            'species': 'Haematococcus',
            'status': 'active',
            'reactor_id': reactor_id,
            'start_date': '2026-04-17',
            'volume_l': 1.8,
        },
    )
    charge_id = create_response.json()['id']

    status_response = client.patch(
        f'/api/v1/charges/{charge_id}/status',
        json={'status': 'completed'},
    )

    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'completed'


def test_create_charge_rejects_missing_reactor(client):
    response = client.post(
        '/api/v1/charges',
        json={
            'name': 'Charge-013',
            'species': 'Chlorella',
            'status': 'planned',
            'reactor_id': 99999,
            'start_date': '2026-04-17',
            'volume_l': 1.0,
        },
    )

    assert response.status_code == 422
    assert response.json()['detail'] == 'Referenced reactor does not exist'


def test_get_charge_returns_404_for_unknown_id(client):
    response = client.get('/api/v1/charges/99999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Charge not found'
