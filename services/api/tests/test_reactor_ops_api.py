from fastapi.testclient import TestClient
from sqlmodel import Session

from app import db
from app.models import Reactor

PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR'
    b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00'
    b'\x90wS\xde'
    b'\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00'
    b'\x18\xdd\x8d\xb1'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def login(client: TestClient, username: str, password: str):
    return client.post('/api/v1/auth/login', json={'username': username, 'password': password})


def test_create_reactor_twin_and_get_detail(client: TestClient):
    with Session(db.engine) as session:
        reactor = Reactor(
            name='Twin Seed Reactor',
            reactor_type='column',
            status='online',
            volume_l=4.2,
            location='Lab West',
            notes='Created directly for ReactorOps POST coverage',
        )
        session.add(reactor)
        session.commit()
        session.refresh(reactor)
        reactor_id = reactor.id

    create_response = client.post(
        '/api/v1/reactor-ops',
        json={
            'reactor_id': reactor_id,
            'culture_type': 'Spirulina',
            'strain': 'SP-X',
            'medium_recipe': 'Medium Twin',
            'inoculated_at': '2026-04-15T09:00:00',
            'current_phase': 'growth',
            'target_ph_min': 8.4,
            'target_ph_max': 9.1,
            'target_temp_min': 29.0,
            'target_temp_max': 33.0,
            'target_light_min': 180.0,
            'target_light_max': 260.0,
            'target_flow_min': 0.6,
            'target_flow_max': 1.2,
            'expected_harvest_window_start': '2026-04-20T08:00:00',
            'expected_harvest_window_end': '2026-04-22T18:00:00',
            'contamination_state': None,
            'technical_state': 'nominal',
            'biological_state': 'growing',
            'notes': 'Primary digital twin config',
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['reactor_id'] == reactor_id
    assert created['culture_type'] == 'Spirulina'
    assert created['technical_state'] == 'nominal'
    assert created['biological_state'] == 'growing'
    assert created['is_configured'] is True

    detail_response = client.get(f'/api/v1/reactor-ops/{reactor_id}')
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['reactor_name'] == 'Twin Seed Reactor'
    assert detail['target_ph_min'] == 8.4
    assert detail['target_flow_max'] == 1.2
    assert detail['recent_events'] == []


def test_update_reactor_twin_and_validate_ranges(client: TestClient):
    create_reactor_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Ops Reactor',
            'reactor_type': 'panel',
            'status': 'online',
            'volume_l': 2.4,
            'location': 'Ops Bay',
            'notes': 'Auto twin should exist',
        },
    )
    reactor_id = create_reactor_response.json()['id']

    update_response = client.put(
        f'/api/v1/reactor-ops/{reactor_id}',
        json={
            'culture_type': 'Chlorella vulgaris',
            'strain': 'CV-17',
            'medium_recipe': 'Medium Green',
            'inoculated_at': '2026-04-14T10:15:00',
            'current_phase': 'harvest_ready',
            'target_ph_min': 7.1,
            'target_ph_max': 7.8,
            'target_temp_min': 24.0,
            'target_temp_max': 27.5,
            'target_light_min': 140.0,
            'target_light_max': 210.0,
            'target_flow_min': 0.4,
            'target_flow_max': 0.7,
            'expected_harvest_window_start': '2026-04-19T09:00:00',
            'expected_harvest_window_end': '2026-04-20T20:00:00',
            'contamination_state': 'cleared',
            'technical_state': 'warning',
            'biological_state': 'stable',
            'notes': 'Ready for harvest check',
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['current_phase'] == 'harvest_ready'
    assert updated['contamination_state'] == 'cleared'
    assert updated['technical_state'] == 'warning'

    invalid_response = client.put(
        f'/api/v1/reactor-ops/{reactor_id}',
        json={
            'culture_type': 'Chlorella vulgaris',
            'strain': 'CV-17',
            'medium_recipe': 'Medium Green',
            'inoculated_at': None,
            'current_phase': 'growth',
            'target_ph_min': 9.2,
            'target_ph_max': 8.0,
            'target_temp_min': None,
            'target_temp_max': None,
            'target_light_min': None,
            'target_light_max': None,
            'target_flow_min': None,
            'target_flow_max': None,
            'expected_harvest_window_start': None,
            'expected_harvest_window_end': None,
            'contamination_state': None,
            'technical_state': 'nominal',
            'biological_state': 'growing',
            'notes': None,
        },
    )
    assert invalid_response.status_code == 422


def test_create_and_list_reactor_events(client: TestClient):
    create_reactor_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Event Reactor',
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 3.1,
            'location': 'Rack Events',
        },
    )
    reactor_id = create_reactor_response.json()['id']

    update_twin_response = client.patch(
        f'/api/v1/reactor-ops/{reactor_id}/phase',
        json={'current_phase': 'stabilization'},
    )
    assert update_twin_response.status_code == 200

    event_response = client.post(
        f'/api/v1/reactors/{reactor_id}/events',
        json={
            'event_type': 'medium_change',
            'title': 'Mediumwechsel ausgefuehrt',
            'description': '20 Prozent Medium ersetzt und Belueftung nachjustiert.',
            'severity': 'warning',
            'phase_snapshot': None,
        },
    )
    assert event_response.status_code == 201
    created_event = event_response.json()
    assert created_event['event_type'] == 'medium_change'
    assert created_event['phase_snapshot'] == 'stabilization'
    assert created_event['created_by_username'] == 'admin'

    list_response = client.get(f'/api/v1/reactors/{reactor_id}/events')
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload[0]['title'] == 'Mediumwechsel ausgefuehrt'
    assert payload[0]['reactor_name'] == 'Event Reactor'


def test_reactor_ops_overview_includes_related_counts(client: TestClient):
    create_reactor_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Aggregated Reactor',
            'reactor_type': 'bag',
            'status': 'online',
            'volume_l': 1.9,
            'location': 'Ops Shelf',
        },
    )
    reactor_id = create_reactor_response.json()['id']

    task_response = client.post(
        '/api/v1/tasks',
        json={
            'title': 'Aggregated Reactor Task',
            'status': 'open',
            'priority': 'high',
            'reactor_id': reactor_id,
        },
    )
    assert task_response.status_code == 201

    alert_response = client.post(
        '/api/v1/alerts',
        json={
            'title': 'Aggregated Reactor Alert',
            'message': 'Manual reactor attention alert',
            'severity': 'warning',
            'status': 'open',
            'source_type': 'reactor',
            'source_id': reactor_id,
        },
    )
    assert alert_response.status_code == 201

    photo_response = client.post(
        '/api/v1/photos/upload',
        data={'title': 'Aggregated Reactor Photo', 'reactor_id': str(reactor_id)},
        files={'file': ('reactor.png', PNG_BYTES, 'image/png')},
    )
    assert photo_response.status_code == 201

    event_response = client.post(
        f'/api/v1/reactors/{reactor_id}/events',
        json={
            'event_type': 'observation',
            'title': 'Aggregated Reactor Observation',
            'description': 'Operational snapshot for overview counts',
            'severity': 'info',
            'phase_snapshot': 'growth',
        },
    )
    assert event_response.status_code == 201

    overview_response = client.get('/api/v1/reactor-ops')
    assert overview_response.status_code == 200
    overview_item = next(item for item in overview_response.json() if item['reactor_id'] == reactor_id)
    assert overview_item['open_task_count'] == 1
    assert overview_item['open_alert_count'] == 1
    assert overview_item['photo_count'] == 1
    assert overview_item['latest_event']['title'] == 'Aggregated Reactor Observation'

    detail_response = client.get(f'/api/v1/reactor-ops/{reactor_id}')
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail['open_tasks'][0]['title'] == 'Aggregated Reactor Task'
    assert detail['recent_alerts'][0]['title'] == 'Aggregated Reactor Alert'
    assert detail['recent_photos'][0]['title'] == 'Aggregated Reactor Photo'
    assert detail['recent_events'][0]['title'] == 'Aggregated Reactor Observation'


def test_viewer_cannot_write_reactor_ops_or_events(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'reactorviewer',
            'display_name': 'Reactor Viewer',
            'email': 'reactorviewer@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201

    create_reactor_response = client.post(
        '/api/v1/reactors',
        json={
            'name': 'Viewer Reactor',
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'Viewer Bay',
        },
    )
    reactor_id = create_reactor_response.json()['id']

    login_response = login(anonymous_client, 'reactorviewer', 'viewerpass')
    assert login_response.status_code == 200

    update_response = anonymous_client.put(
        f'/api/v1/reactor-ops/{reactor_id}',
        json={
            'culture_type': 'Viewer Test',
            'strain': None,
            'medium_recipe': None,
            'inoculated_at': None,
            'current_phase': 'growth',
            'target_ph_min': None,
            'target_ph_max': None,
            'target_temp_min': None,
            'target_temp_max': None,
            'target_light_min': None,
            'target_light_max': None,
            'target_flow_min': None,
            'target_flow_max': None,
            'expected_harvest_window_start': None,
            'expected_harvest_window_end': None,
            'contamination_state': None,
            'technical_state': 'nominal',
            'biological_state': 'unknown',
            'notes': None,
        },
    )
    assert update_response.status_code == 403
    assert update_response.json()['detail'] == 'Operator role required'

    event_response = anonymous_client.post(
        f'/api/v1/reactors/{reactor_id}/events',
        json={
            'event_type': 'observation',
            'title': 'Viewer should not write',
            'description': None,
            'severity': None,
            'phase_snapshot': None,
        },
    )
    assert event_response.status_code == 403
    assert event_response.json()['detail'] == 'Operator role required'
