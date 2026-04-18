def test_create_label_and_get_by_code(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Prusa MK4',
            'asset_type': 'printer_3d',
            'category': 'MakerOps',
            'status': 'active',
            'location': 'Werkbank 1',
            'zone': 'Maker Corner',
        },
    )
    assert asset_response.status_code == 201
    asset_id = asset_response.json()['id']

    create_response = client.post(
        '/api/v1/labels',
        json={
            'label_code': '  ast-prusa-mk4  ',
            'label_type': 'qr',
            'target_type': 'asset',
            'target_id': asset_id,
            'display_name': '  Prusa MK4 QR  ',
            'location_snapshot': '  Werkbank 1 / Maker Corner  ',
            'note': '  Front panel  ',
            'is_active': True,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['label_code'] == 'AST-PRUSA-MK4'
    assert created['target_type'] == 'asset'
    assert created['target_id'] == asset_id
    assert created['display_name'] == 'Prusa MK4 QR'
    assert created['location_snapshot'] == 'Werkbank 1 / Maker Corner'
    assert created['note'] == 'Front panel'
    assert created['target_name'] == 'Prusa MK4'
    assert created['target_location'] == 'Werkbank 1 / Maker Corner'
    assert created['scan_path'] == '/scan/AST-PRUSA-MK4'

    read_response = client.get('/api/v1/labels/AST-PRUSA-MK4')
    assert read_response.status_code == 200
    assert read_response.json()['id'] == created['id']


def test_auto_generate_label_code_and_uniqueness(client):
    item_response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Isopropanol',
            'category': 'chemical',
            'status': 'available',
            'quantity': 2,
            'unit': 'l',
            'location': 'Chemikalienschrank',
        },
    )
    assert item_response.status_code == 201
    item_id = item_response.json()['id']

    create_response = client.post(
        '/api/v1/labels',
        json={
            'target_type': 'inventory_item',
            'target_id': item_id,
            'label_type': 'qr',
        },
    )
    assert create_response.status_code == 201
    generated_code = create_response.json()['label_code']
    assert generated_code.startswith('LBL-INV-')

    duplicate_response = client.post(
        '/api/v1/labels',
        json={
            'label_code': generated_code,
            'target_type': 'inventory_item',
            'target_id': item_id,
            'label_type': 'qr',
        },
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()['detail'] == 'Label code already exists'


def test_label_target_resolution_for_asset_and_inventory(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Mikroskop Nordbank',
            'asset_type': 'microscope',
            'category': 'BioOps',
            'status': 'maintenance',
            'location': 'Laborbank Nord',
            'zone': 'Wet Lab',
        },
    )
    assert asset_response.status_code == 201
    asset_id = asset_response.json()['id']

    label_asset = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-AST-MICRO',
            'target_type': 'asset',
            'target_id': asset_id,
            'label_type': 'qr',
        },
    )
    assert label_asset.status_code == 201

    asset_target = client.get('/api/v1/labels/LBL-AST-MICRO/target')
    assert asset_target.status_code == 200
    payload = asset_target.json()
    assert payload['label']['label_code'] == 'LBL-AST-MICRO'
    assert payload['asset']['id'] == asset_id
    assert payload['inventory_item'] is None

    item_response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'PLA Filament schwarz',
            'category': 'filament',
            'status': 'available',
            'quantity': 1.5,
            'unit': 'kg',
            'location': 'Werkbank 1',
        },
    )
    assert item_response.status_code == 201
    item_id = item_response.json()['id']

    label_inventory = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-INV-PLA',
            'target_type': 'inventory_item',
            'target_id': item_id,
            'label_type': 'qr',
        },
    )
    assert label_inventory.status_code == 201

    inventory_target = client.get('/api/v1/labels/LBL-INV-PLA/target')
    assert inventory_target.status_code == 200
    inventory_payload = inventory_target.json()
    assert inventory_payload['inventory_item']['id'] == item_id
    assert inventory_payload['asset'] is None


def test_update_label_and_toggle_active(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Server1',
            'asset_type': 'server',
            'category': 'ITOps',
            'status': 'active',
            'location': 'Rack A',
        },
    )
    asset_id = asset_response.json()['id']

    label_response = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-AST-SERVER1-TEST',
            'target_type': 'asset',
            'target_id': asset_id,
            'label_type': 'qr',
        },
    )
    assert label_response.status_code == 201
    label_id = label_response.json()['id']

    update_response = client.put(
        f'/api/v1/labels/{label_id}',
        json={
            'label_code': 'LBL-AST-SERVER1-RACK',
            'label_type': 'printed_label',
            'target_type': 'asset',
            'target_id': asset_id,
            'display_name': 'Server Rack Label',
            'location_snapshot': 'Rack A',
            'note': 'Top rack rail',
            'is_active': True,
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['label_code'] == 'LBL-AST-SERVER1-RACK'
    assert updated['label_type'] == 'printed_label'
    assert updated['display_name'] == 'Server Rack Label'

    inactive_response = client.patch(
        f'/api/v1/labels/{label_id}/active',
        json={'is_active': False},
    )
    assert inactive_response.status_code == 200
    assert inactive_response.json()['is_active'] is False


def test_label_filters_and_overview(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Pumpe A',
            'asset_type': 'pump',
            'category': 'BioOps',
            'status': 'active',
            'location': 'Fluidik Rack',
        },
    )
    asset_id = asset_response.json()['id']

    item_response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Ersatzduese MK4',
            'category': 'spare_part',
            'status': 'available',
            'quantity': 3,
            'unit': 'pcs',
            'location': 'Werkbank 1',
        },
    )
    item_id = item_response.json()['id']

    first_label = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-AST-PUMP-A',
            'target_type': 'asset',
            'target_id': asset_id,
            'label_type': 'qr',
        },
    )
    assert first_label.status_code == 201

    second_label = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-INV-NOZZLE',
            'target_type': 'inventory_item',
            'target_id': item_id,
            'label_type': 'qr',
            'is_active': False,
        },
    )
    assert second_label.status_code == 201

    filtered = client.get(
        '/api/v1/labels',
        params={'target_type': 'asset', 'active': 'true', 'target_id': asset_id},
    )
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert len(filtered_payload) == 1
    assert filtered_payload[0]['label_code'] == 'LBL-AST-PUMP-A'

    overview = client.get('/api/v1/labels/overview')
    assert overview.status_code == 200
    overview_payload = overview.json()
    assert overview_payload['labeled_assets'] >= 1
    assert overview_payload['labeled_inventory_items'] >= 0
    assert any(label['label_code'] == 'LBL-INV-NOZZLE' for label in overview_payload['recent_labels'])


def test_label_qr_endpoint_returns_svg(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': 'Odroid N2+',
            'asset_type': 'sbc',
            'category': 'Automation',
            'status': 'active',
            'location': 'Regal Sued',
        },
    )
    asset_id = asset_response.json()['id']

    label_response = client.post(
        '/api/v1/labels',
        json={
            'label_code': 'LBL-AST-ODROID',
            'target_type': 'asset',
            'target_id': asset_id,
            'label_type': 'qr',
        },
    )
    assert label_response.status_code == 201

    qr_response = client.get('/api/v1/labels/LBL-AST-ODROID/qr')
    assert qr_response.status_code == 200
    assert qr_response.headers['content-type'].startswith('image/svg+xml')
    assert '<svg' in qr_response.text
