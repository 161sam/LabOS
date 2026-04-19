from datetime import timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import db
from app.models import (
    Photo,
    Reactor,
    ReactorHealthAssessment,
    ReactorTwin,
    SafetyIncident,
    TelemetryValue,
    VisionAnalysis,
    _utcnow,
)
from app.services import reactor_health as reactor_health_service


def _make_reactor(session: Session, name: str) -> int:
    reactor = Reactor(name=name, reactor_type='mobil', status='online', volume_l=1.5, location='Lab')
    session.add(reactor)
    session.commit()
    session.refresh(reactor)
    return reactor.id


def _make_twin(session: Session, reactor_id: int, **targets) -> ReactorTwin:
    twin = ReactorTwin(reactor_id=reactor_id, current_phase='growth', **targets)
    session.add(twin)
    session.commit()
    session.refresh(twin)
    return twin


def _make_telemetry(session: Session, reactor_id: int, sensor_type: str, value: float, unit: str,
                    *, minutes_ago: int = 1) -> TelemetryValue:
    ts = _utcnow() - timedelta(minutes=minutes_ago)
    tv = TelemetryValue(
        reactor_id=reactor_id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        source='device',
        timestamp=ts,
    )
    session.add(tv)
    session.commit()
    session.refresh(tv)
    return tv


def _make_vision(session: Session, reactor_id: int, *, health_label: str, confidence: float = 0.8,
                 green_ratio: float = 0.4) -> VisionAnalysis:
    photo = Photo(
        filename='test.jpg',
        original_filename='test.jpg',
        mime_type='image/jpeg',
        size_bytes=10,
        storage_path='photos/test.jpg',
        reactor_id=reactor_id,
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)
    va = VisionAnalysis(
        photo_id=photo.id,
        reactor_id=reactor_id,
        analysis_type='lab_photo_basic',
        status='ok',
        result={'health_label': health_label, 'green_ratio': green_ratio, 'sharpness': 0.3},
        confidence=confidence,
    )
    session.add(va)
    session.commit()
    session.refresh(va)
    return va


def test_assessment_nominal_when_telemetry_and_vision_match(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Nominal')
        _make_twin(session, reactor_id, target_temp_min=20.0, target_temp_max=30.0,
                   target_ph_min=7.0, target_ph_max=8.0)
        _make_telemetry(session, reactor_id, 'temp', 25.0, 'C')
        _make_telemetry(session, reactor_id, 'ph', 7.5, '')
        _make_vision(session, reactor_id, health_label='healthy_green')

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'nominal'
    assert any(sig['code'] == 'telemetry_nominal' for sig in body['signals'])


def test_assessment_attention_on_low_biomass_vision(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Attention')
        _make_twin(session, reactor_id, target_temp_min=20.0, target_temp_max=30.0)
        _make_telemetry(session, reactor_id, 'temp', 25.0, 'C')
        _make_vision(session, reactor_id, health_label='low_biomass', green_ratio=0.05)

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'attention'
    assert any(sig['code'] == 'vision_green_ratio_drop' for sig in body['signals'])


def test_assessment_warning_on_telemetry_out_of_range_and_contamination(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Warning')
        _make_twin(session, reactor_id, target_temp_min=20.0, target_temp_max=28.0)
        _make_telemetry(session, reactor_id, 'temp', 33.0, 'C')
        _make_vision(session, reactor_id, health_label='contamination_suspected')

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'warning'
    codes = {sig['code'] for sig in body['signals']}
    assert 'telemetry_temp_above_range' in codes
    assert 'vision_contamination_suspected' in codes


def test_assessment_incident_when_critical_safety_open(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Incident')
        _make_telemetry(session, reactor_id, 'temp', 25.0, 'C')
        session.add(SafetyIncident(
            reactor_id=reactor_id,
            incident_type='overheating_risk',
            severity='critical',
            status='open',
            title='Kritische Ueberhitzung',
        ))
        session.commit()

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'incident'
    assert any(sig['code'] == 'safety_critical_incident_open' for sig in body['signals'])


def test_assessment_unknown_when_no_data(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Unknown')

    response = client.post(f'/api/v1/reactor-health/{reactor_id}/assess')
    assert response.status_code == 201
    body = response.json()
    assert body['status'] == 'unknown'


def test_list_and_get_latest_endpoints(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-List')
        _make_telemetry(session, reactor_id, 'temp', 25.0, 'C')

    client.post(f'/api/v1/reactor-health/{reactor_id}/assess')

    latest = client.get(f'/api/v1/reactor-health/{reactor_id}')
    assert latest.status_code == 200
    assert latest.json()['reactor_id'] == reactor_id

    history = client.get(f'/api/v1/reactor-health/{reactor_id}/history')
    assert history.status_code == 200
    assert len(history.json()) >= 1

    listing = client.get('/api/v1/reactor-health')
    assert listing.status_code == 200
    assert any(item['reactor_id'] == reactor_id for item in listing.json())


def test_count_by_status_covers_all_reactors(client: TestClient):
    with Session(db.engine) as session:
        reactor_a_id = _make_reactor(session, 'Health-CountA')
        _make_reactor(session, 'Health-CountB')
        _make_telemetry(session, reactor_a_id, 'temp', 25.0, 'C')

    client.post(f'/api/v1/reactor-health/{reactor_a_id}/assess')

    with Session(db.engine) as session:
        counts = reactor_health_service.count_by_status(session)

    assert counts['unknown'] >= 1


def test_reactor_twin_exposes_latest_health(client: TestClient):
    with Session(db.engine) as session:
        reactor_id = _make_reactor(session, 'Health-Twin')
        _make_twin(session, reactor_id, target_temp_min=20.0, target_temp_max=30.0)
        _make_telemetry(session, reactor_id, 'temp', 25.0, 'C')

    client.post(f'/api/v1/reactor-health/{reactor_id}/assess')

    overview = client.get(f'/api/v1/reactor-ops/{reactor_id}')
    assert overview.status_code == 200
    body = overview.json()
    assert body['latest_health'] is not None
    assert body['latest_health']['reactor_id'] == reactor_id
