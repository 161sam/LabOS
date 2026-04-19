import io

from PIL import Image


def _build_png(size=(8, 8), color=(60, 200, 80)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGB', size, color=color).save(buffer, format='PNG')
    return buffer.getvalue()


def _seed_reactor_id(client) -> int:
    response = client.get('/api/v1/reactors')
    return response.json()[0]['id']


def test_upload_creates_vision_analysis_automatically(client):
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('green.png', _build_png(color=(40, 210, 70)), 'image/png')},
    )
    assert upload.status_code == 201
    photo = upload.json()
    assert photo['latest_vision'] is not None
    assert photo['latest_vision']['status'] == 'ok'
    result = photo['latest_vision']['result']
    assert result['width'] == 8
    assert result['height'] == 8
    assert 'avg_rgb' in result
    assert 'brightness' in result
    assert 'green_ratio' in result
    assert result['green_ratio'] > 0.5
    assert result['health_label'] in {'healthy_green', 'growing'}


def test_vision_endpoint_returns_latest_analysis(client):
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('snap.png', _build_png(), 'image/png')},
    )
    photo_id = upload.json()['id']

    response = client.get(f'/api/v1/vision/photos/{photo_id}')
    assert response.status_code == 200
    payload = response.json()
    assert payload['photo_id'] == photo_id
    assert payload['status'] == 'ok'
    assert payload['analysis_type'] == 'basic'
    assert payload['result']['width'] == 8


def test_vision_endpoint_404_for_photo_without_analysis(client):
    response = client.get('/api/v1/vision/photos/9999')
    assert response.status_code == 404


def test_manual_reanalyze_creates_new_analysis(client):
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('frame.png', _build_png(), 'image/png')},
    )
    photo_id = upload.json()['id']

    rerun = client.post(f'/api/v1/vision/analyze/{photo_id}')
    assert rerun.status_code == 201
    history = client.get(f'/api/v1/vision/photos/{photo_id}/history')
    assert history.status_code == 200
    analyses = history.json()
    assert len(analyses) >= 2
    assert all(item['photo_id'] == photo_id for item in analyses)


def test_vision_classification_detects_dark_frame(client):
    dark_png = _build_png(color=(4, 4, 4))
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('dark.png', dark_png, 'image/png')},
    )
    analysis = upload.json()['latest_vision']
    assert analysis['result']['health_label'] == 'too_dark'


def test_vision_classification_detects_contamination_suspected(client):
    brown_png = _build_png(color=(180, 110, 60))
    upload = client.post(
        '/api/v1/photos/upload',
        files={'file': ('brown.png', brown_png, 'image/png')},
    )
    analysis = upload.json()['latest_vision']
    assert analysis['result']['brown_ratio'] > 0.1
    assert analysis['result']['health_label'] in {'contamination_suspected', 'low_biomass', 'no_growth_visible'}


def test_reactor_twin_includes_latest_vision(client):
    reactor_id = _seed_reactor_id(client)
    upload = client.post(
        '/api/v1/photos/upload',
        data={'reactor_id': str(reactor_id)},
        files={'file': ('reactor.png', _build_png(), 'image/png')},
    )
    assert upload.status_code == 201

    twins = client.get('/api/v1/reactor-ops')
    assert twins.status_code == 200
    reactor_twin = next(twin for twin in twins.json() if twin['reactor_id'] == reactor_id)
    assert reactor_twin['latest_vision'] is not None
    assert reactor_twin['latest_vision']['result']['health_label']


def test_abrain_context_photo_section_carries_vision_metrics(client):
    reactor_id = _seed_reactor_id(client)
    client.post(
        '/api/v1/photos/upload',
        data={'reactor_id': str(reactor_id), 'title': 'Sample with vision'},
        files={'file': ('abrain.png', _build_png(), 'image/png')},
    )

    context = client.get('/api/v1/abrain/context', params={'include_sections': 'photos'})
    assert context.status_code == 200
    photos = context.json()['photos']
    assert photos is not None and len(photos) >= 1
    first = photos[0]
    assert 'vision_health_label' in first
    assert first['vision_health_label']
