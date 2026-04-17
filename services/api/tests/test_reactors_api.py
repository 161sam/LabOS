def test_create_and_get_reactor(client):
    create_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Reaktor-B2',
            'reactor_type': 'tower',
            'status': 'offline',
            'volume_l': 3.4,
            'location': 'Regal B',
            'last_cleaned_at': '2026-04-16T10:30:00',
            'notes': '  Gereinigt und bereit  ',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'Reaktor-B2'
    assert created['reactor_type'] == 'tower'
    assert created['status'] == 'offline'
    assert created['location'] == 'Regal B'
    assert created['notes'] == 'Gereinigt und bereit'

    get_response = client.get(f"/api/v1/reactors/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_update_reactor(client):
    create_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Reaktor-C1',
            'reactor_type': 'bag',
            'status': 'online',
            'volume_l': 2.2,
            'location': 'Labor 1',
            'last_cleaned_at': '2026-04-15T09:00:00',
            'notes': 'Im Betrieb',
        },
    )
    reactor_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/reactors/{reactor_id}',
        json={
            'name': 'Reaktor-C1-Prime',
            'reactor_type': 'panel',
            'status': 'maintenance',
            'volume_l': 2.8,
            'location': 'Labor 2',
            'last_cleaned_at': '2026-04-17T08:15:00',
            'notes': '',
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['name'] == 'Reaktor-C1-Prime'
    assert updated['reactor_type'] == 'panel'
    assert updated['status'] == 'maintenance'
    assert updated['location'] == 'Labor 2'
    assert updated['notes'] is None


def test_change_reactor_status(client):
    create_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Reaktor-D1',
            'reactor_type': 'mobil',
            'status': 'online',
            'volume_l': 1.6,
        },
    )
    reactor_id = create_response.json()['id']

    status_response = client.patch(
        f'/api/v1/reactors/{reactor_id}/status',
        json={'status': 'cleaning'},
    )

    assert status_response.status_code == 200
    assert status_response.json()['status'] == 'cleaning'


def test_create_reactor_rejects_invalid_volume(client):
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Reaktor-E1',
            'reactor_type': 'bag',
            'status': 'online',
            'volume_l': 0,
        },
    )

    assert response.status_code == 422


def test_get_reactor_returns_404_for_unknown_id(client):
    response = client.get('/api/v1/reactors/99999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Reactor not found'
