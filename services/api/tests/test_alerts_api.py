def test_create_and_get_alert(client):
    create_response = client.post(
        '/api/v1/alerts',
        json={
            'title': '  Temperatur Warnung  ',
            'message': '  Medium liegt ueber Soll  ',
            'severity': 'high',
            'status': 'open',
            'source_type': 'sensor',
            'source_id': 1,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['title'] == 'Temperatur Warnung'
    assert created['message'] == 'Medium liegt ueber Soll'
    assert created['severity'] == 'high'
    assert created['status'] == 'open'

    get_response = client.get(f"/api/v1/alerts/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_acknowledge_alert(client):
    create_response = client.post(
        '/api/v1/alerts',
        json={
            'title': 'Sensor ohne Werte',
            'message': 'Sensor liefert keine Werte',
            'severity': 'warning',
            'source_type': 'sensor',
        },
    )
    alert_id = create_response.json()['id']

    ack_response = client.patch(f'/api/v1/alerts/{alert_id}/ack')
    assert ack_response.status_code == 200
    acknowledged = ack_response.json()
    assert acknowledged['status'] == 'acknowledged'
    assert acknowledged['acknowledged_at'] is not None


def test_resolve_alert(client):
    create_response = client.post(
        '/api/v1/alerts',
        json={
            'title': 'pH kritisch',
            'message': 'pH liegt ausserhalb des zulassigen Bereichs',
            'severity': 'critical',
            'source_type': 'sensor',
        },
    )
    alert_id = create_response.json()['id']

    resolve_response = client.patch(f'/api/v1/alerts/{alert_id}/resolve')
    assert resolve_response.status_code == 200
    resolved = resolve_response.json()
    assert resolved['status'] == 'resolved'
    assert resolved['acknowledged_at'] is not None
    assert resolved['resolved_at'] is not None


def test_alert_filters_by_status_and_severity(client):
    client.post(
        '/api/v1/alerts',
        json={
            'title': 'Filter Alert Info',
            'message': 'Info alert',
            'severity': 'info',
            'source_type': 'manual',
        },
    )
    critical = client.post(
        '/api/v1/alerts',
        json={
            'title': 'Filter Alert Critical',
            'message': 'Critical alert',
            'severity': 'critical',
            'source_type': 'manual',
        },
    )
    critical_id = critical.json()['id']
    client.patch(f'/api/v1/alerts/{critical_id}/resolve')

    severity_response = client.get('/api/v1/alerts', params={'severity': 'critical'})
    assert severity_response.status_code == 200
    assert all(alert['severity'] == 'critical' for alert in severity_response.json())

    status_response = client.get('/api/v1/alerts', params={'status': 'resolved'})
    assert status_response.status_code == 200
    assert all(alert['status'] == 'resolved' for alert in status_response.json())


def test_get_alert_returns_404_for_unknown_id(client):
    response = client.get('/api/v1/alerts/99999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Alert not found'
