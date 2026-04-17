def _seed_charge_id(client) -> int:
    response = client.get('/api/v1/charges')
    assert response.status_code == 200
    return response.json()[0]['id']


def _seed_reactor_id(client) -> int:
    response = client.get('/api/v1/reactors')
    assert response.status_code == 200
    return response.json()[0]['id']


def _seed_asset_id(client) -> int:
    response = client.get('/api/v1/assets')
    assert response.status_code == 200
    return response.json()[0]['id']


def test_create_and_get_task(client):
    charge_id = _seed_charge_id(client)
    reactor_id = _seed_reactor_id(client)
    asset_id = _seed_asset_id(client)
    create_response = client.post(
        '/api/v1/tasks',
        json={
            'title': '  Probe fuer Charge-002  ',
            'description': '  Zellzahl und pH pruefen  ',
            'status': 'open',
            'priority': 'high',
            'due_at': '2026-04-18T08:30:00',
            'charge_id': charge_id,
            'reactor_id': reactor_id,
            'asset_id': asset_id,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['title'] == 'Probe fuer Charge-002'
    assert created['description'] == 'Zellzahl und pH pruefen'
    assert created['priority'] == 'high'
    assert created['charge_id'] == charge_id
    assert created['reactor_id'] == reactor_id
    assert created['asset_id'] == asset_id
    assert created['charge_name']
    assert created['reactor_name']
    assert created['asset_name']

    get_response = client.get(f"/api/v1/tasks/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_update_task(client):
    asset_id = _seed_asset_id(client)
    create_response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Reaktor pruefen',
            'description': 'Erste Version',
            'status': 'open',
            'priority': 'normal',
        },
    )
    task_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/tasks/{task_id}',
        json={
            'title': 'Reaktor pruefen und dokumentieren',
            'description': ' ',
            'status': 'blocked',
            'priority': 'critical',
            'due_at': '2026-04-19T10:00:00',
            'charge_id': None,
            'reactor_id': None,
            'asset_id': asset_id,
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['title'] == 'Reaktor pruefen und dokumentieren'
    assert updated['description'] is None
    assert updated['status'] == 'blocked'
    assert updated['priority'] == 'critical'
    assert updated['due_at'] == '2026-04-19T10:00:00'
    assert updated['asset_id'] == asset_id


def test_change_task_status_sets_completed_at(client):
    create_response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Reinigung abschliessen',
            'status': 'doing',
            'priority': 'normal',
        },
    )
    task_id = create_response.json()['id']

    done_response = client.patch(
        f'/api/v1/tasks/{task_id}/status',
        json={'status': 'done'},
    )

    assert done_response.status_code == 200
    done_task = done_response.json()
    assert done_task['status'] == 'done'
    assert done_task['completed_at'] is not None

    reopen_response = client.patch(
        f'/api/v1/tasks/{task_id}/status',
        json={'status': 'open'},
    )
    assert reopen_response.status_code == 200
    assert reopen_response.json()['completed_at'] is None


def test_task_filters_by_status_and_priority(client):
    asset_id = _seed_asset_id(client)
    client.post(
        '/api/v1/tasks',
        json={
            'title': 'Filter Task Open',
            'status': 'open',
            'priority': 'critical',
            'asset_id': asset_id,
        },
    )
    client.post(
        '/api/v1/tasks',
        json={
            'title': 'Filter Task Done',
            'status': 'done',
            'priority': 'low',
        },
    )

    status_response = client.get('/api/v1/tasks', params={'status': 'done'})
    assert status_response.status_code == 200
    assert all(task['status'] == 'done' for task in status_response.json())

    priority_response = client.get('/api/v1/tasks', params={'priority': 'critical'})
    assert priority_response.status_code == 200
    assert all(task['priority'] == 'critical' for task in priority_response.json())

    asset_response = client.get('/api/v1/tasks', params={'asset_id': asset_id})
    assert asset_response.status_code == 200
    assert all(task['asset_id'] == asset_id for task in asset_response.json())


def test_create_task_rejects_missing_charge(client):
    response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Ungueltige Zuordnung',
            'status': 'open',
            'priority': 'normal',
            'charge_id': 99999,
        },
    )

    assert response.status_code == 422
    assert response.json()['detail'] == 'Referenced charge does not exist'


def test_create_task_rejects_missing_asset(client):
    response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Ungueltige Asset-Zuordnung',
            'status': 'open',
            'priority': 'normal',
            'asset_id': 99999,
        },
    )

    assert response.status_code == 422
    assert response.json()['detail'] == 'Referenced asset does not exist'
