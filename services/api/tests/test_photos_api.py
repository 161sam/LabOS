import io

from PIL import Image


def _build_png(size=(1, 1), color=(90, 180, 60)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', size, color=color).save(buffer, format='PNG')
    return buffer.getvalue()


PNG_BYTES = _build_png()


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


def test_upload_photo_and_get_detail(client):
    charge_id = _seed_charge_id(client)
    reactor_id = _seed_reactor_id(client)
    asset_id = _seed_asset_id(client)

    response = client.post(
        '/api/v1/photos/upload',
        data={
            'title': '  Charge Blick oben  ',
            'notes': '  Farbe und Schaumbild pruefen  ',
            'charge_id': str(charge_id),
            'reactor_id': str(reactor_id),
            'asset_id': str(asset_id),
            'uploaded_by': '  lab-tech  ',
            'captured_at': '2026-04-17T10:30:00',
        },
        files={'file': ('sample.png', PNG_BYTES, 'image/png')},
    )

    assert response.status_code == 201
    created = response.json()
    assert created['title'] == 'Charge Blick oben'
    assert created['notes'] == 'Farbe und Schaumbild pruefen'
    assert created['uploaded_by'] == 'lab-tech'
    assert created['mime_type'] == 'image/png'
    assert created['size_bytes'] == len(PNG_BYTES)
    assert created['charge_id'] == charge_id
    assert created['reactor_id'] == reactor_id
    assert created['asset_id'] == asset_id
    assert created['storage_path'].startswith('photos/')
    assert created['file_url'] == f"/api/v1/photos/{created['id']}/file"

    detail = client.get(f"/api/v1/photos/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()['id'] == created['id']


def test_upload_photo_rejects_invalid_type(client):
    response = client.post(
        '/api/v1/photos/upload',
        files={'file': ('notes.txt', b'not-an-image', 'text/plain')},
    )

    assert response.status_code == 415
    assert 'Unsupported photo type' in response.json()['detail']


def test_list_photos_can_filter_by_charge_and_reactor(client):
    charge_id = _seed_charge_id(client)
    reactor_id = _seed_reactor_id(client)
    asset_id = _seed_asset_id(client)

    first = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Charge Foto', 'charge_id': str(charge_id)},
        files={'file': ('charge.png', PNG_BYTES, 'image/png')},
    )
    assert first.status_code == 201

    second = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Reaktor Foto', 'reactor_id': str(reactor_id)},
        files={'file': ('reactor.png', PNG_BYTES, 'image/png')},
    )
    assert second.status_code == 201

    third = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Asset Foto', 'asset_id': str(asset_id)},
        files={'file': ('asset.png', PNG_BYTES, 'image/png')},
    )
    assert third.status_code == 201

    by_charge = client.get('/api/v1/photos', params={'charge_id': charge_id})
    assert by_charge.status_code == 200
    assert all(photo['charge_id'] == charge_id for photo in by_charge.json())

    by_reactor = client.get('/api/v1/photos', params={'reactor_id': reactor_id})
    assert by_reactor.status_code == 200
    assert all(photo['reactor_id'] == reactor_id for photo in by_reactor.json())

    by_asset = client.get('/api/v1/photos', params={'asset_id': asset_id})
    assert by_asset.status_code == 200
    assert all(photo['asset_id'] == asset_id for photo in by_asset.json())


def test_photo_file_serving_returns_binary_content(client):
    upload = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Dokufoto'},
        files={'file': ('doc.png', PNG_BYTES, 'image/png')},
    )
    photo_id = upload.json()['id']

    file_response = client.get(f'/api/v1/photos/{photo_id}/file')
    assert file_response.status_code == 200
    assert file_response.headers['content-type'] == 'image/png'
    assert file_response.content == PNG_BYTES


def test_update_photo_metadata(client):
    charge_id = _seed_charge_id(client)
    reactor_id = _seed_reactor_id(client)
    asset_id = _seed_asset_id(client)

    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('meta.png', PNG_BYTES, 'image/png')},
    )
    photo_id = upload.json()['id']

    update = client.put(
        f'/api/v1/photos/{photo_id}',
        json={
            'title': '  Neues Foto Label  ',
            'notes': '  Dokumentation aktualisiert  ',
            'charge_id': charge_id,
            'reactor_id': reactor_id,
            'asset_id': asset_id,
            'uploaded_by': '  operator-1  ',
            'captured_at': '2026-04-17T12:45:00',
        },
    )

    assert update.status_code == 200
    updated = update.json()
    assert updated['title'] == 'Neues Foto Label'
    assert updated['notes'] == 'Dokumentation aktualisiert'
    assert updated['uploaded_by'] == 'operator-1'
    assert updated['charge_id'] == charge_id
    assert updated['reactor_id'] == reactor_id
    assert updated['asset_id'] == asset_id


def test_photo_analysis_status_returns_vision_result(client):
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('analysis.png', PNG_BYTES, 'image/png')},
    )
    photo_id = upload.json()['id']
    assert upload.json()['latest_vision'] is not None

    response = client.get(f'/api/v1/photos/{photo_id}/analysis-status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['photo_id'] == photo_id
    assert payload['status'] == 'ok'
    assert payload['latest_vision'] is not None
    assert payload['latest_vision']['result']['width'] == 1
    assert payload['latest_vision']['result']['health_label']
