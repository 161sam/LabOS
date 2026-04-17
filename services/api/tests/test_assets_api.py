PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR'
    b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00'
    b'\x90wS\xde'
    b'\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00'
    b'\x18\xdd\x8d\xb1'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def test_create_and_get_asset(client):
    create_response = client.post(
        '/api/v1/assets',
        json={
            'name': '  SLA Printer Bench  ',
            'asset_type': 'printer_3d',
            'category': '  MakerOps  ',
            'status': 'active',
            'location': '  Werkbank Ost  ',
            'zone': '  Print Zone  ',
            'serial_number': '  SLA-001  ',
            'manufacturer': '  Formlabs  ',
            'model': '  Form 3  ',
            'notes': '  Harzstand pruefen  ',
            'maintenance_notes': '  Tank regelmaessig inspizieren  ',
            'last_maintenance_at': '2026-04-10T09:00:00',
            'next_maintenance_at': '2026-04-25T09:00:00',
            'wiki_ref': '  devices/sla-printer  ',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'SLA Printer Bench'
    assert created['category'] == 'MakerOps'
    assert created['location'] == 'Werkbank Ost'
    assert created['zone'] == 'Print Zone'
    assert created['serial_number'] == 'SLA-001'
    assert created['manufacturer'] == 'Formlabs'
    assert created['model'] == 'Form 3'
    assert created['notes'] == 'Harzstand pruefen'
    assert created['maintenance_notes'] == 'Tank regelmaessig inspizieren'
    assert created['wiki_ref'] == 'devices/sla-printer'
    assert created['open_task_count'] == 0
    assert created['photo_count'] == 0

    detail_response = client.get(f"/api/v1/assets/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['id'] == created['id']
    assert detail['open_tasks'] == []
    assert detail['recent_photos'] == []


def test_update_asset(client):
    create_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Bench PSU',
            'asset_type': 'power_supply',
            'category': 'MakerOps',
            'status': 'inactive',
            'location': 'Elektronikplatz',
        },
    )
    asset_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/assets/{asset_id}',
        json={
            'name': 'Bench PSU 30V',
            'asset_type': 'power_supply',
            'category': 'Electronics',
            'status': 'maintenance',
            'location': 'Elektronikplatz',
            'zone': 'Maker Corner',
            'serial_number': None,
            'manufacturer': 'Rigol',
            'model': 'DP832',
            'notes': '  Kalibrierung geplant  ',
            'maintenance_notes': '  Luefter reinigen  ',
            'last_maintenance_at': '2026-04-11T08:00:00',
            'next_maintenance_at': '2026-04-21T08:00:00',
            'wiki_ref': 'assets/bench-psu-30v',
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['name'] == 'Bench PSU 30V'
    assert updated['category'] == 'Electronics'
    assert updated['status'] == 'maintenance'
    assert updated['manufacturer'] == 'Rigol'
    assert updated['model'] == 'DP832'
    assert updated['notes'] == 'Kalibrierung geplant'
    assert updated['maintenance_notes'] == 'Luefter reinigen'


def test_change_asset_status(client):
    create_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Edge Router',
            'asset_type': 'network_device',
            'category': 'ITOps',
            'status': 'active',
            'location': 'Rack B',
        },
    )
    asset_id = create_response.json()['id']

    response = client.patch(
        f'/api/v1/assets/{asset_id}/status',
        json={'status': 'error'},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'error'


def test_asset_filters_and_overview(client):
    created = client.post(
        '/api/v1/assets',
        json={
            'name': 'Scope Bench',
            'asset_type': 'tool',
            'category': 'RD Ops',
            'status': 'maintenance',
            'location': 'Lab Tisch 2',
            'zone': 'Diagnostics',
            'next_maintenance_at': '2026-04-22T10:00:00',
        },
    )
    assert created.status_code == 201
    asset_id = created.json()['id']

    filtered = client.get(
        '/api/v1/assets',
        params={
            'status': 'maintenance',
            'category': 'RD Ops',
            'location': 'Lab Tisch',
            'zone': 'Diag',
        },
    )
    assert filtered.status_code == 200
    assert any(asset['id'] == asset_id for asset in filtered.json())

    overview = client.get('/api/v1/assets/overview')
    assert overview.status_code == 200
    payload = overview.json()
    assert payload['assets_in_maintenance'] >= 1
    assert any(asset['id'] == asset_id for asset in payload['upcoming_maintenance_assets'])


def test_asset_detail_includes_tasks_and_photos(client):
    create_asset = client.post(
        '/api/v1/assets',
        json={
            'name': 'Pump Bench A',
            'asset_type': 'pump',
            'category': 'BioOps',
            'status': 'active',
            'location': 'Fluidik Rack',
        },
    )
    asset_id = create_asset.json()['id']

    task_response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Pumpenschlauch pruefen',
            'status': 'open',
            'priority': 'high',
            'asset_id': asset_id,
        },
    )
    assert task_response.status_code == 201

    photo_response = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Pumpenfoto', 'asset_id': str(asset_id)},
        files={'file': ('pump.png', PNG_BYTES, 'image/png')},
    )
    assert photo_response.status_code == 201

    detail = client.get(f'/api/v1/assets/{asset_id}')
    assert detail.status_code == 200
    payload = detail.json()
    assert payload['open_task_count'] == 1
    assert payload['photo_count'] == 1
    assert payload['open_tasks'][0]['asset_id'] == asset_id
    assert payload['recent_photos'][0]['asset_id'] == asset_id
