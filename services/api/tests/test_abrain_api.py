import httpx

from app.config import settings
from app.services import abrain_adapter, abrain_client

PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR'
    b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00'
    b'\x90wS\xde'
    b'\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00'
    b'\x18\xdd\x8d\xb1'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def test_get_abrain_status_returns_stub_metadata(client):
    response = client.get('/api/v1/abrain/status')

    assert response.status_code == 200
    payload = response.json()
    assert payload['connected'] is False
    assert payload['mode'] == 'stub'
    assert payload['fallback_available'] is True


def test_get_abrain_presets_returns_expected_entries(client):
    response = client.get('/api/v1/abrain/presets')

    assert response.status_code == 200
    presets = response.json()
    preset_ids = {preset['id'] for preset in presets}
    assert {
        'daily_overview',
        'critical_issues',
        'overdue_tasks',
        'sensor_attention',
        'reactor_attention',
        'recent_activity',
    } <= preset_ids


def test_get_abrain_context_returns_structured_lab_context(client):
    client.post(
        '/api/v1/photos/upload',
        data={'title': 'ABrain Kontext Foto'},
        files={'file': ('context.png', PNG_BYTES, 'image/png')},
    )

    response = client.get('/api/v1/abrain/context', params=[('include_sections', 'tasks'), ('include_sections', 'photos')])

    assert response.status_code == 200
    payload = response.json()
    assert payload['included_sections'] == ['tasks', 'photos']
    assert payload['summary']['open_tasks'] >= 1
    assert payload['tasks'] is not None
    assert payload['photos'] is not None
    assert payload['alerts'] is None


def test_post_abrain_query_returns_consistent_response_structure(client):
    response = client.post(
        '/api/v1/abrain/query',
        json={
            'question': 'Welche kritischen Themen brauchen gerade Aufmerksamkeit?',
            'preset': 'critical_issues',
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['preset'] == 'critical_issues'
    assert payload['mode'] == 'stub'
    assert isinstance(payload['summary'], str) and payload['summary']
    assert isinstance(payload['highlights'], list)
    assert isinstance(payload['recommended_actions'], list)
    assert isinstance(payload['referenced_entities'], list)
    assert set(payload['used_context_sections']) >= {'alerts', 'sensors'}


def test_post_abrain_query_falls_back_when_external_connector_fails(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')
    monkeypatch.setattr(settings, 'abrain_use_local_fallback', True)

    monkeypatch.setattr(
        abrain_client,
        'query',
        lambda request_payload: abrain_client.ABrainClientResult(
            success=False, payload=None, mode='external', error='offline'
        ),
    )

    response = client.post(
        '/api/v1/abrain/query',
        json={
            'question': 'Gib mir den Tagesueberblick.',
            'preset': 'daily_overview',
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['mode'] == 'stub'
    assert payload['fallback_used'] is True
    assert 'Lokale Assistenzlogik' in payload['note']


def test_legacy_query_delegates_through_adapter(client, monkeypatch):
    calls: list[str] = []
    original = abrain_adapter.query_adapter

    def spy(session, payload):
        calls.append(payload.question)
        return original(session, payload)

    monkeypatch.setattr(abrain_adapter, 'query_adapter', spy)
    response = client.post(
        '/api/v1/abrain/query',
        json={'question': 'Adapter-Proxy-Check', 'preset': 'daily_overview'},
    )
    assert response.status_code == 200
    assert calls == ['Adapter-Proxy-Check'], 'legacy /abrain/query must delegate to abrain_adapter'


def test_abrain_status_marks_external_connector_unreachable(client, monkeypatch):
    monkeypatch.setattr(settings, 'abrain_use_stub', False)
    monkeypatch.setattr(settings, 'abrain_enabled', True)
    monkeypatch.setattr(settings, 'abrain_mode', 'external')

    class BrokenClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, *args, **kwargs):
            raise httpx.ConnectError('offline')

    monkeypatch.setattr(abrain_client.httpx, 'Client', BrokenClient)

    response = client.get('/api/v1/abrain/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['connected'] is False
    assert payload['mode'] == 'external'
