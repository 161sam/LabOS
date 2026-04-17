from app.config import settings


def _seed_sensor_by_name(client, name: str):
    response = client.get('/api/v1/sensors')
    assert response.status_code == 200
    return next(sensor for sensor in response.json() if sensor['name'] == name)


def _seed_reactor_id(client) -> int:
    response = client.get('/api/v1/reactors')
    assert response.status_code == 200
    return response.json()[0]['id']


def test_create_rule_and_get_rule(client):
    sensor = _seed_sensor_by_name(client, 'Mediumtemperatur A1')
    create_response = client.post(
        '/api/v1/rules',
        json={
            'name': '  Temperatur zu hoch Test  ',
            'description': '  Erzeugt Alert bei hoher Temperatur  ',
            'is_enabled': True,
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 23.5},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Regel {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'high',
                'source_type': 'sensor',
            },
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'Temperatur zu hoch Test'
    assert created['description'] == 'Erzeugt Alert bei hoher Temperatur'

    get_response = client.get(f"/api/v1/rules/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == created['id']


def test_create_rule_rejects_invalid_configuration(client):
    response = client.post(
        '/api/v1/rules',
        json={
            'name': 'Invalid Rule',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'count_gt',
            'condition_config': {'count': 1},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Invalid',
                'message_template': 'Invalid',
                'severity': 'warning',
            },
        },
    )

    assert response.status_code == 422


def test_rule_dry_run_evaluation_logs_match_without_side_effect(client):
    sensor = _seed_sensor_by_name(client, 'Mediumtemperatur A1')
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Dry Run Temperatur',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 23.5},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Dry Run Alert {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'high',
                'source_type': 'sensor',
            },
        },
    ).json()

    alerts_before = client.get('/api/v1/alerts').json()
    evaluate_response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=true")
    assert evaluate_response.status_code == 200
    payload = evaluate_response.json()
    assert payload['execution']['status'] == 'matched'
    assert payload['execution']['dry_run'] is True

    alerts_after = client.get('/api/v1/alerts').json()
    assert len(alerts_after) == len(alerts_before)


def test_rule_execution_can_create_alert(client):
    sensor = _seed_sensor_by_name(client, 'Mediumtemperatur A1')
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Temperatur Alert Execute',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 23.5},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Executed Alert {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'high',
                'source_type': 'sensor',
            },
        },
    ).json()

    evaluate_response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=false")
    assert evaluate_response.status_code == 200
    payload = evaluate_response.json()
    assert payload['execution']['status'] == 'executed'
    assert payload['execution']['action_result']['executed'] is True
    assert payload['execution']['action_result']['entity_type'] == 'alert'


def test_rule_execution_can_create_task(client):
    sensor = _seed_sensor_by_name(client, 'pH Sonde A1')
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'pH Task Execute',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_lt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 7.0},
            'action_type': 'create_task',
            'action_config': {
                'title_template': 'Task {sensor_name}',
                'description_template': 'Bitte {sensor_name} pruefen',
                'priority': 'high',
                'reactor_id': '{reactor_id}',
                'due_in_hours': 2,
            },
        },
    ).json()

    evaluate_response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=false")
    assert evaluate_response.status_code == 200
    payload = evaluate_response.json()
    assert payload['execution']['status'] == 'executed'
    assert payload['execution']['action_result']['entity_type'] == 'task'


def test_stale_sensor_rule_matches_sensor_without_values(client):
    reactor_id = _seed_reactor_id(client)
    sensor_response = client.post(
        '/api/v1/sensors',
        json={
            'name': 'Stale Sensor Test',
            'sensor_type': 'temperature',
            'unit': '°C',
            'status': 'active',
            'reactor_id': reactor_id,
        },
    )
    sensor_id = sensor_response.json()['id']

    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Stale Sensor Rule',
            'trigger_type': 'stale_sensor',
            'condition_type': 'age_gt_hours',
            'condition_config': {'sensor_id': sensor_id, 'hours': 1},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Stale {sensor_name}',
                'message_template': 'Seit {hours}h kein Wert',
                'severity': 'warning',
                'source_type': 'sensor',
            },
        },
    ).json()

    evaluate_response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=true")
    assert evaluate_response.status_code == 200
    assert evaluate_response.json()['execution']['status'] == 'matched'


def test_overdue_tasks_rule_matches_and_creates_alert(client):
    client.post(
        '/api/v1/tasks',
        json={
            'title': 'Ueberfaellig fuer Regeltest',
            'status': 'open',
            'priority': 'normal',
            'due_at': '2026-04-16T08:00:00',
        },
    )
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Overdue Task Alert',
            'trigger_type': 'overdue_tasks',
            'condition_type': 'count_gt',
            'condition_config': {'count': 0, 'overdue_by_hours': 0},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Overdue {count}',
                'message_template': 'Aelteste Aufgabe: {oldest_task_title}',
                'severity': 'warning',
                'source_type': 'system',
            },
        },
    ).json()

    evaluate_response = client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=false")
    assert evaluate_response.status_code == 200
    payload = evaluate_response.json()
    assert payload['execution']['status'] == 'executed'
    assert payload['execution']['evaluation_summary']['overdue_task_count'] >= 1


def test_rule_execution_log_endpoints(client):
    sensor = _seed_sensor_by_name(client, 'Mediumtemperatur A1')
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Log Retrieval Rule',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 23.5},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Log {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'high',
                'source_type': 'sensor',
            },
        },
    ).json()

    client.post(f"/api/v1/rules/{rule['id']}/evaluate?dry_run=true")

    by_rule = client.get(f"/api/v1/rules/{rule['id']}/executions")
    assert by_rule.status_code == 200
    assert len(by_rule.json()) >= 1
    assert all(execution['rule_id'] == rule['id'] for execution in by_rule.json())

    all_logs = client.get('/api/v1/rules/executions')
    assert all_logs.status_code == 200
    assert len(all_logs.json()) >= 1


def test_rule_status_toggle(client):
    sensor = _seed_sensor_by_name(client, 'Mediumtemperatur A1')
    rule = client.post(
        '/api/v1/rules',
        json={
            'name': 'Toggle Rule',
            'trigger_type': 'sensor_threshold',
            'condition_type': 'threshold_gt',
            'condition_config': {'sensor_id': sensor['id'], 'threshold': 23.5},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Toggle {sensor_name}',
                'message_template': 'Wert {value}',
                'severity': 'high',
                'source_type': 'sensor',
            },
        },
    ).json()

    response = client.patch(f"/api/v1/rules/{rule['id']}/enabled", json={'is_enabled': False})
    assert response.status_code == 200
    assert response.json()['is_enabled'] is False
