"""Tests for Calibration / Maintenance / Safety V1."""

import pytest


def _create_reactor(client):
    response = client.post(
        '/api/v1/reactors',
        json={'name': 'Test-Reaktor', 'reactor_type': 'mobil', 'status': 'online', 'volume_l': 1.0},
    )
    assert response.status_code == 201
    return response.json()


def _create_device_node(client, reactor_id=None):
    payload = {'name': 'Test-Node', 'node_type': 'sensor_bridge', 'status': 'online'}
    if reactor_id:
        payload['reactor_id'] = reactor_id
    response = client.post('/api/v1/devices', json=payload)
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------


def test_create_calibration_record(client):
    reactor = _create_reactor(client)
    response = client.post(
        '/api/v1/calibration',
        json={
            'target_type': 'reactor',
            'target_id': reactor['id'],
            'parameter': 'ph',
            'status': 'valid',
            'calibration_value': 7.01,
            'reference_value': 7.00,
            'note': '  pH-Kalibrierung OK  ',
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['parameter'] == 'ph'
    assert data['status'] == 'valid'
    assert data['note'] == 'pH-Kalibrierung OK'
    assert data['target_name'] == reactor['name']


def test_update_calibration_record(client):
    reactor = _create_reactor(client)
    create_response = client.post(
        '/api/v1/calibration',
        json={'target_type': 'reactor', 'target_id': reactor['id'], 'parameter': 'temp', 'status': 'unknown'},
    )
    record_id = create_response.json()['id']

    update_response = client.patch(
        f'/api/v1/calibration/{record_id}',
        json={'status': 'expired', 'note': 'Kalibrierung abgelaufen'},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['status'] == 'expired'
    assert updated['note'] == 'Kalibrierung abgelaufen'


def test_calibration_list_filter_by_status(client):
    reactor = _create_reactor(client)
    client.post('/api/v1/calibration', json={'target_type': 'reactor', 'target_id': reactor['id'], 'parameter': 'ph', 'status': 'valid'})
    client.post('/api/v1/calibration', json={'target_type': 'reactor', 'target_id': reactor['id'], 'parameter': 'temp', 'status': 'expired'})

    expired = client.get('/api/v1/calibration', params={'status': 'expired'})
    assert expired.status_code == 200
    assert all(r['status'] == 'expired' for r in expired.json())

    valid = client.get('/api/v1/calibration', params={'status': 'valid'})
    assert valid.status_code == 200
    assert all(r['status'] == 'valid' for r in valid.json())


def test_calibration_overview(client):
    reactor = _create_reactor(client)
    client.post('/api/v1/calibration', json={'target_type': 'reactor', 'target_id': reactor['id'], 'parameter': 'ph', 'status': 'expired'})
    client.post('/api/v1/calibration', json={'target_type': 'reactor', 'target_id': reactor['id'], 'parameter': 'temp', 'status': 'valid'})

    response = client.get('/api/v1/calibration/overview')
    assert response.status_code == 200
    data = response.json()
    assert data['expired'] >= 1
    assert data['valid'] >= 1
    assert data['due_or_expired'] >= 1


def test_calibration_requires_auth(anonymous_client):
    response = anonymous_client.post(
        '/api/v1/calibration',
        json={'target_type': 'reactor', 'target_id': 1, 'parameter': 'ph'},
    )
    assert response.status_code == 401


def test_calibration_record_404_for_unknown_target(client):
    response = client.post(
        '/api/v1/calibration',
        json={'target_type': 'reactor', 'target_id': 99999, 'parameter': 'ph'},
    )
    assert response.status_code == 404


def test_calibration_record_update_404(client):
    response = client.patch('/api/v1/calibration/99999', json={'status': 'valid'})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------


def test_create_maintenance_record(client):
    reactor = _create_reactor(client)
    response = client.post(
        '/api/v1/maintenance',
        json={
            'target_type': 'reactor',
            'target_id': reactor['id'],
            'maintenance_type': 'cleaning',
            'status': 'scheduled',
            'note': '  Woechentliche Reinigung  ',
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['maintenance_type'] == 'cleaning'
    assert data['status'] == 'scheduled'
    assert data['note'] == 'Woechentliche Reinigung'
    assert data['target_name'] == reactor['name']


def test_update_maintenance_record(client):
    reactor = _create_reactor(client)
    create_response = client.post(
        '/api/v1/maintenance',
        json={'target_type': 'reactor', 'target_id': reactor['id'], 'maintenance_type': 'inspection', 'status': 'scheduled'},
    )
    record_id = create_response.json()['id']

    update_response = client.patch(
        f'/api/v1/maintenance/{record_id}',
        json={'status': 'done', 'note': 'Abgeschlossen'},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['status'] == 'done'


def test_maintenance_list_filter_by_status(client):
    reactor = _create_reactor(client)
    client.post('/api/v1/maintenance', json={'target_type': 'reactor', 'target_id': reactor['id'], 'maintenance_type': 'cleaning', 'status': 'overdue'})
    client.post('/api/v1/maintenance', json={'target_type': 'reactor', 'target_id': reactor['id'], 'maintenance_type': 'inspection', 'status': 'done'})

    overdue = client.get('/api/v1/maintenance', params={'status': 'overdue'})
    assert overdue.status_code == 200
    assert all(r['status'] == 'overdue' for r in overdue.json())


def test_maintenance_overview(client):
    reactor = _create_reactor(client)
    client.post('/api/v1/maintenance', json={'target_type': 'reactor', 'target_id': reactor['id'], 'maintenance_type': 'cleaning', 'status': 'overdue'})

    response = client.get('/api/v1/maintenance/overview')
    assert response.status_code == 200
    data = response.json()
    assert data['overdue'] >= 1
    assert data['total'] >= 1


def test_maintenance_requires_auth(anonymous_client):
    response = anonymous_client.post(
        '/api/v1/maintenance',
        json={'target_type': 'reactor', 'target_id': 1, 'maintenance_type': 'cleaning'},
    )
    assert response.status_code == 401


def test_maintenance_record_update_404(client):
    response = client.patch('/api/v1/maintenance/99999', json={'status': 'done'})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Safety Incidents
# ---------------------------------------------------------------------------


def test_create_safety_incident(client):
    reactor = _create_reactor(client)
    response = client.post(
        '/api/v1/safety/incidents',
        json={
            'incident_type': 'calibration_expired',
            'severity': 'high',
            'title': '  pH Kalibrierung abgelaufen  ',
            'description': 'pH-Sonde seit 90 Tagen nicht kalibriert',
            'reactor_id': reactor['id'],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['incident_type'] == 'calibration_expired'
    assert data['severity'] == 'high'
    assert data['status'] == 'open'
    assert data['title'] == 'pH Kalibrierung abgelaufen'
    assert data['reactor_name'] == reactor['name']


def test_acknowledge_and_resolve_incident(client):
    create_response = client.post(
        '/api/v1/safety/incidents',
        json={'incident_type': 'node_offline', 'severity': 'warning', 'title': 'Test node offline'},
    )
    incident_id = create_response.json()['id']

    ack = client.patch(f'/api/v1/safety/incidents/{incident_id}', json={'status': 'acknowledged'})
    assert ack.status_code == 200
    assert ack.json()['status'] == 'acknowledged'

    resolved = client.patch(f'/api/v1/safety/incidents/{incident_id}', json={'status': 'resolved'})
    assert resolved.status_code == 200
    assert resolved.json()['status'] == 'resolved'
    assert resolved.json()['resolved_at'] is not None


def test_incident_list_filter_by_status(client):
    client.post('/api/v1/safety/incidents', json={'incident_type': 'general', 'severity': 'info', 'title': 'Open incident'})
    resolved_resp = client.post('/api/v1/safety/incidents', json={'incident_type': 'general', 'severity': 'info', 'title': 'Resolved incident'})
    client.patch(f'/api/v1/safety/incidents/{resolved_resp.json()["id"]}', json={'status': 'resolved'})

    open_list = client.get('/api/v1/safety/incidents', params={'status': 'open'})
    assert open_list.status_code == 200
    assert all(i['status'] == 'open' for i in open_list.json())

    resolved_list = client.get('/api/v1/safety/incidents', params={'status': 'resolved'})
    assert resolved_list.status_code == 200
    assert all(i['status'] == 'resolved' for i in resolved_list.json())


def test_safety_overview(client):
    client.post('/api/v1/safety/incidents', json={'incident_type': 'general', 'severity': 'critical', 'title': 'Critical incident'})

    response = client.get('/api/v1/safety/overview')
    assert response.status_code == 200
    data = response.json()
    assert data['open_incidents'] >= 1
    assert data['critical_incidents'] >= 1
    assert 'blocked_commands' in data
    assert 'calibration_expired' in data
    assert 'maintenance_overdue' in data


def test_incident_requires_auth(anonymous_client):
    response = anonymous_client.post(
        '/api/v1/safety/incidents',
        json={'incident_type': 'general', 'severity': 'info', 'title': 'Unauthorized'},
    )
    assert response.status_code == 401


def test_incident_update_404(client):
    response = client.patch('/api/v1/safety/incidents/99999', json={'status': 'resolved'})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Command Guard Logic
# ---------------------------------------------------------------------------


def test_command_blocked_by_critical_incident(client):
    reactor = _create_reactor(client)

    client.post(
        '/api/v1/safety/incidents',
        json={
            'incident_type': 'dry_run_risk',
            'severity': 'critical',
            'title': 'Critical dry run risk',
            'reactor_id': reactor['id'],
        },
    )

    command_response = client.post(
        f'/api/v1/reactors/{reactor["id"]}/commands',
        json={'command_type': 'pump_on'},
    )
    assert command_response.status_code == 201
    cmd = command_response.json()
    assert cmd['status'] == 'blocked'
    assert cmd['blocked_reason'] is not None
    assert 'critical' in cmd['blocked_reason'].lower() or 'blocked' in cmd['blocked_reason'].lower()


def test_command_not_blocked_without_incidents(client):
    reactor = _create_reactor(client)

    command_response = client.post(
        f'/api/v1/reactors/{reactor["id"]}/commands',
        json={'command_type': 'light_on'},
    )
    assert command_response.status_code == 201
    cmd = command_response.json()
    assert cmd['status'] in ('pending', 'sent', 'failed')
    assert cmd['blocked_reason'] is None


def test_command_blocked_by_dry_run_incident(client):
    reactor = _create_reactor(client)

    client.post(
        '/api/v1/safety/incidents',
        json={
            'incident_type': 'dry_run_risk',
            'severity': 'warning',
            'title': 'Pump dry run risk',
            'reactor_id': reactor['id'],
        },
    )

    pump_response = client.post(
        f'/api/v1/reactors/{reactor["id"]}/commands',
        json={'command_type': 'pump_on'},
    )
    assert pump_response.status_code == 201
    cmd = pump_response.json()
    assert cmd['status'] == 'blocked'


def test_command_not_blocked_light_with_dry_run_incident(client):
    reactor = _create_reactor(client)

    client.post(
        '/api/v1/safety/incidents',
        json={
            'incident_type': 'dry_run_risk',
            'severity': 'warning',
            'title': 'Dry run risk for pump',
            'reactor_id': reactor['id'],
        },
    )

    light_response = client.post(
        f'/api/v1/reactors/{reactor["id"]}/commands',
        json={'command_type': 'light_on'},
    )
    assert light_response.status_code == 201
    assert light_response.json()['status'] != 'blocked'


def test_command_blocked_by_offline_node_for_pump(client):
    reactor = _create_reactor(client)
    node = _create_device_node(client, reactor_id=reactor['id'])

    client.patch(f'/api/v1/devices/{node["id"]}', json={'status': 'offline'})

    pump_response = client.post(
        f'/api/v1/reactors/{reactor["id"]}/commands',
        json={'command_type': 'pump_on'},
    )
    assert pump_response.status_code == 201
    assert pump_response.json()['status'] == 'blocked'


def test_blocked_command_appears_in_list(client):
    reactor = _create_reactor(client)

    client.post(
        '/api/v1/safety/incidents',
        json={'incident_type': 'general', 'severity': 'critical', 'title': 'Block all', 'reactor_id': reactor['id']},
    )
    client.post(f'/api/v1/reactors/{reactor["id"]}/commands', json={'command_type': 'aeration_start'})

    commands = client.get(f'/api/v1/reactors/{reactor["id"]}/commands')
    assert commands.status_code == 200
    blocked = [c for c in commands.json() if c['status'] == 'blocked']
    assert len(blocked) >= 1
