def test_create_and_get_inventory_item(client):
    asset_response = client.post(
        '/api/v1/assets',
        json={
            'name': '  Prusa Shelf  ',
            'asset_type': 'printer_3d',
            'category': '  MakerOps  ',
            'status': 'active',
            'location': '  Werkbank 2  ',
        },
    )
    assert asset_response.status_code == 201
    asset_id = asset_response.json()['id']

    create_response = client.post(
        '/api/v1/inventory',
        json={
            'name': '  PLA Filament Schwarz  ',
            'category': '  filament  ',
            'status': 'available',
            'quantity': 0.75,
            'unit': '  kg  ',
            'min_quantity': 1.0,
            'location': '  Regal Maker  ',
            'zone': '  Druckbereich  ',
            'supplier': '  Prusa  ',
            'sku': '  FIL-001  ',
            'notes': '  fuer Gehaeuse  ',
            'asset_id': asset_id,
            'wiki_ref': '  materials/pla-black  ',
            'last_restocked_at': '2026-04-15T09:00:00',
            'expiry_date': '2027-04-15',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'PLA Filament Schwarz'
    assert created['category'] == 'filament'
    assert created['unit'] == 'kg'
    assert created['location'] == 'Regal Maker'
    assert created['zone'] == 'Druckbereich'
    assert created['supplier'] == 'Prusa'
    assert created['sku'] == 'FIL-001'
    assert created['notes'] == 'fuer Gehaeuse'
    assert created['wiki_ref'] == 'materials/pla-black'
    assert created['status'] == 'low_stock'
    assert created['is_low_stock'] is True
    assert created['needs_restock'] is True
    assert created['asset_id'] == asset_id
    assert created['asset_name'] == 'Prusa Shelf'

    detail_response = client.get(f"/api/v1/inventory/{created['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['id'] == created['id']
    assert detail['asset_name'] == 'Prusa Shelf'


def test_update_inventory_item_and_out_of_stock_logic(client):
    create_response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Isopropanol',
            'category': 'cleaning_supply',
            'status': 'available',
            'quantity': 2.0,
            'unit': 'l',
            'min_quantity': 0.5,
            'location': 'Chemikalienschrank',
        },
    )
    item_id = create_response.json()['id']

    update_response = client.put(
        f'/api/v1/inventory/{item_id}',
        json={
            'name': 'Isopropanol 99%',
            'category': 'chemical',
            'status': 'available',
            'quantity': 0,
            'unit': 'l',
            'min_quantity': 0.5,
            'location': 'Chemikalienschrank',
            'zone': 'Wet Lab',
            'supplier': 'Carl Roth',
            'sku': 'IPA-99',
            'notes': '  fuer Reinigung und Bench Prep  ',
            'asset_id': None,
            'wiki_ref': 'materials/isopropanol',
            'last_restocked_at': '2026-04-10T08:00:00',
            'expiry_date': '2027-04-10',
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['name'] == 'Isopropanol 99%'
    assert updated['category'] == 'chemical'
    assert updated['status'] == 'out_of_stock'
    assert updated['is_out_of_stock'] is True
    assert updated['needs_restock'] is True
    assert updated['notes'] == 'fuer Reinigung und Bench Prep'


def test_change_inventory_status(client):
    create_response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'JST Kabelsatz',
            'category': 'cable',
            'status': 'available',
            'quantity': 5,
            'unit': 'sets',
            'min_quantity': 2,
            'location': 'Elektronikplatz',
        },
    )
    item_id = create_response.json()['id']

    reserved_response = client.patch(
        f'/api/v1/inventory/{item_id}/status',
        json={'status': 'reserved'},
    )
    assert reserved_response.status_code == 200
    assert reserved_response.json()['status'] == 'reserved'

    back_to_available = client.patch(
        f'/api/v1/inventory/{item_id}/status',
        json={'status': 'available'},
    )
    assert back_to_available.status_code == 200
    assert back_to_available.json()['status'] == 'available'


def test_inventory_filters_and_overview(client):
    low_stock_item = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Naehrmedium A',
            'category': 'nutrient',
            'status': 'available',
            'quantity': 0.4,
            'unit': 'l',
            'min_quantity': 0.5,
            'location': 'Kuehlschrank Nord',
            'zone': 'Wet Lab',
            'supplier': 'Lab Internal',
            'sku': 'MED-A',
        },
    )
    assert low_stock_item.status_code == 201

    out_of_stock_item = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Schrumpfschlauch Set',
            'category': 'electronic_component',
            'status': 'available',
            'quantity': 0,
            'unit': 'sets',
            'min_quantity': 1,
            'location': 'Elektronikplatz',
            'zone': 'Maker Corner',
            'supplier': 'Maker Supply',
            'sku': 'SHRINK-01',
        },
    )
    assert out_of_stock_item.status_code == 201

    normal_item = client.post(
        '/api/v1/inventory',
        json={
            'name': 'M3 Schrauben',
            'category': 'screw',
            'status': 'available',
            'quantity': 200,
            'unit': 'pcs',
            'min_quantity': 80,
            'location': 'Kleinteilewand',
            'zone': 'Maker Corner',
        },
    )
    assert normal_item.status_code == 201

    filtered = client.get(
        '/api/v1/inventory',
        params={
            'low_stock': 'true',
            'location': 'platz',
            'zone': 'Maker',
            'search': 'SHRINK',
        },
    )
    assert filtered.status_code == 200
    filtered_ids = {item['id'] for item in filtered.json()}
    assert out_of_stock_item.json()['id'] in filtered_ids
    assert low_stock_item.json()['id'] not in filtered_ids

    overview = client.get('/api/v1/inventory/overview')
    assert overview.status_code == 200
    payload = overview.json()
    assert payload['total_items'] >= 3
    assert payload['low_stock_items'] >= 1
    assert payload['out_of_stock_items'] >= 1
    critical_ids = {item['id'] for item in payload['critical_items']}
    assert low_stock_item.json()['id'] in critical_ids or out_of_stock_item.json()['id'] in critical_ids


def test_inventory_rejects_unknown_asset_reference(client):
    response = client.post(
        '/api/v1/inventory',
        json={
            'name': 'Ersatzteil X',
            'category': 'spare_part',
            'status': 'available',
            'quantity': 1,
            'unit': 'pcs',
            'location': 'Regal A',
            'asset_id': 9999,
        },
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'Asset not found'
