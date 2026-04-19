from datetime import timedelta
from pathlib import Path

from alembic import command
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from app.db import get_alembic_config
from app.models import Reactor, Rule, Schedule, ScheduleExecution, _utcnow
from app.services import scheduler as scheduler_service


def create_reactor(client: TestClient, name: str = 'Schedule Reactor') -> int:
    response = client.post(
        '/api/v1/reactors',
        json={
            'name': name,
            'reactor_type': 'tower',
            'status': 'online',
            'volume_l': 2.0,
            'location': 'Sched Bay',
        },
    )
    assert response.status_code == 201
    return response.json()['id']


def create_rule(client: TestClient, name: str = 'Schedule Rule') -> int:
    response = client.post(
        '/api/v1/rules',
        json={
            'name': name,
            'description': 'schedule test rule',
            'is_enabled': True,
            'trigger_type': 'overdue_tasks',
            'condition_type': 'count_gt',
            'condition_config': {'count': 0},
            'action_type': 'create_alert',
            'action_config': {
                'title_template': 'Overdue tasks',
                'message_template': '{count} tasks overdue',
                'severity': 'warning',
            },
        },
    )
    assert response.status_code == 201, response.text
    return response.json()['id']


def create_test_engine(tmp_path: Path):
    db_path = tmp_path / 'scheduler.db'
    database_url = f'sqlite:///{db_path}'
    command.upgrade(get_alembic_config(database_url), 'head')
    return create_engine(database_url, echo=False, connect_args={'check_same_thread': False})


def test_cron_parser_computes_next_occurrence():
    base = _utcnow().replace(second=0, microsecond=0)
    schedule = Schedule(
        name='cron',
        schedule_type='cron',
        cron_expr='*/10 * * * *',
        target_type='rule',
        target_id=1,
    )
    next_run = scheduler_service.compute_next_run(schedule, after=base)
    assert next_run is not None
    assert (next_run - base) <= timedelta(minutes=10)
    assert next_run.minute % 10 == 0


def test_create_schedule_rejects_command_without_reactor(client: TestClient):
    response = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Missing reactor',
            'schedule_type': 'interval',
            'interval_seconds': 60,
            'target_type': 'command',
            'target_params': {'command_type': 'light_on'},
        },
    )
    assert response.status_code == 422


def test_create_and_update_interval_command_schedule(client: TestClient):
    reactor_id = create_reactor(client, 'Interval Reactor')
    create_response = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Light cycle',
            'description': 'alternates light on',
            'schedule_type': 'interval',
            'interval_seconds': 600,
            'target_type': 'command',
            'reactor_id': reactor_id,
            'target_params': {'command_type': 'light_on'},
            'is_enabled': True,
        },
    )
    assert create_response.status_code == 201, create_response.text
    schedule = create_response.json()
    assert schedule['next_run_at'] is not None
    assert schedule['schedule_type'] == 'interval'

    patch_response = client.patch(
        f'/api/v1/schedules/{schedule["id"]}',
        json={
            'name': 'Light cycle (slow)',
            'schedule_type': 'interval',
            'interval_seconds': 1200,
            'target_type': 'command',
            'reactor_id': reactor_id,
            'target_params': {'command_type': 'light_on'},
            'is_enabled': True,
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()['interval_seconds'] == 1200


def test_set_schedule_enabled_clears_next_run(client: TestClient):
    reactor_id = create_reactor(client, 'Toggle Reactor')
    create_response = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Toggle',
            'schedule_type': 'interval',
            'interval_seconds': 60,
            'target_type': 'command',
            'reactor_id': reactor_id,
            'target_params': {'command_type': 'light_on'},
            'is_enabled': True,
        },
    )
    schedule_id = create_response.json()['id']

    disable = client.patch(f'/api/v1/schedules/{schedule_id}/enabled', json={'is_enabled': False})
    assert disable.status_code == 200
    assert disable.json()['is_enabled'] is False
    assert disable.json()['next_run_at'] is None

    enable = client.patch(f'/api/v1/schedules/{schedule_id}/enabled', json={'is_enabled': True})
    assert enable.status_code == 200
    assert enable.json()['next_run_at'] is not None


def test_run_schedule_now_executes_rule(client: TestClient):
    rule_id = create_rule(client, 'Run-now rule')
    create_response = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Rule now',
            'schedule_type': 'manual',
            'target_type': 'rule',
            'target_id': rule_id,
            'target_params': {'dry_run': True},
            'is_enabled': True,
        },
    )
    schedule_id = create_response.json()['id']

    run_response = client.post(f'/api/v1/schedules/{schedule_id}/run')
    assert run_response.status_code == 200
    body = run_response.json()
    assert body['execution']['status'] == 'success'
    assert body['execution']['result']['action'] == 'rule'
    assert body['schedule']['last_run_at'] is not None


def test_find_due_schedules_picks_up_stale_schedule(tmp_path: Path):
    engine = create_test_engine(tmp_path)
    with Session(engine) as session:
        reactor = Reactor(name='Stale', reactor_type='tower', status='online', volume_l=1.0)
        session.add(reactor)
        session.commit()
        session.refresh(reactor)

        stale = Schedule(
            name='Stale interval',
            schedule_type='interval',
            interval_seconds=60,
            target_type='command',
            reactor_id=reactor.id,
            target_params={'command_type': 'light_on'},
            is_enabled=True,
            next_run_at=_utcnow() - timedelta(minutes=5),
        )
        fresh = Schedule(
            name='Fresh interval',
            schedule_type='interval',
            interval_seconds=60,
            target_type='command',
            reactor_id=reactor.id,
            target_params={'command_type': 'light_on'},
            is_enabled=True,
            next_run_at=_utcnow() + timedelta(minutes=5),
        )
        disabled = Schedule(
            name='Disabled',
            schedule_type='interval',
            interval_seconds=60,
            target_type='command',
            reactor_id=reactor.id,
            target_params={'command_type': 'light_on'},
            is_enabled=False,
            next_run_at=_utcnow() - timedelta(minutes=1),
        )
        session.add_all([stale, fresh, disabled])
        session.commit()
        stale_id = stale.id

    with Session(engine) as session:
        due = scheduler_service.find_due_schedules(session)
        assert [s.id for s in due] == [stale_id]


def test_execute_schedule_logs_failure(tmp_path: Path):
    engine = create_test_engine(tmp_path)
    with Session(engine) as session:
        rule = Rule(
            name='schedule-failure',
            is_enabled=True,
            trigger_type='overdue_tasks',
            condition_type='count_gt',
            condition_config={'count': 0},
            action_type='create_alert',
            action_config={
                'title_template': 't',
                'message_template': 'm',
                'severity': 'warning',
            },
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)

        broken = Schedule(
            name='Broken schedule',
            schedule_type='manual',
            target_type='rule',
            target_id=rule.id + 999,
            target_params={'dry_run': True},
            is_enabled=True,
        )
        session.add(broken)
        session.commit()
        session.refresh(broken)
        schedule_id = broken.id

    with Session(engine) as session:
        schedule = session.get(Schedule, schedule_id)
        execution = scheduler_service.execute_schedule(session, schedule, trigger='manual')
        assert execution.status == 'failed'
        assert execution.error

    with Session(engine) as session:
        from sqlmodel import select
        logs = list(session.exec(select(ScheduleExecution).where(ScheduleExecution.schedule_id == schedule_id)))
        assert len(logs) == 1
        assert logs[0].status == 'failed'


def test_tick_runs_due_schedules(tmp_path: Path):
    engine = create_test_engine(tmp_path)
    with Session(engine) as session:
        rule = Rule(
            name='tick-rule',
            is_enabled=True,
            trigger_type='overdue_tasks',
            condition_type='count_gt',
            condition_config={'count': 0},
            action_type='create_alert',
            action_config={
                'title_template': 't',
                'message_template': 'm',
                'severity': 'warning',
            },
        )
        session.add(rule)
        session.commit()
        session.refresh(rule)

        schedule = Schedule(
            name='Tick interval',
            schedule_type='interval',
            interval_seconds=30,
            target_type='rule',
            target_id=rule.id,
            target_params={'dry_run': True},
            is_enabled=True,
            next_run_at=_utcnow() - timedelta(seconds=5),
        )
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
        schedule_id = schedule.id

    with Session(engine) as session:
        executions = scheduler_service.tick(session)
        assert len(executions) == 1
        assert executions[0].schedule_id == schedule_id
        assert executions[0].status == 'success'

    with Session(engine) as session:
        schedule = session.get(Schedule, schedule_id)
        assert schedule.last_run_at is not None
        assert schedule.next_run_at is not None
        assert schedule.next_run_at > schedule.last_run_at


def test_list_executions_endpoint(client: TestClient):
    rule_id = create_rule(client, 'Exec list rule')
    schedule_id = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Exec list',
            'schedule_type': 'manual',
            'target_type': 'rule',
            'target_id': rule_id,
            'target_params': {'dry_run': True},
            'is_enabled': True,
        },
    ).json()['id']

    client.post(f'/api/v1/schedules/{schedule_id}/run')
    client.post(f'/api/v1/schedules/{schedule_id}/run')

    response = client.get(f'/api/v1/schedules/{schedule_id}/executions')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(entry['status'] == 'success' for entry in data)


def test_create_schedule_requires_operator(client: TestClient, anonymous_client: TestClient):
    user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'schedviewer',
            'display_name': 'Sched Viewer',
            'email': 'schedviewer@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert user_response.status_code == 201

    login = anonymous_client.post(
        '/api/v1/auth/login',
        json={'username': 'schedviewer', 'password': 'viewerpass'},
    )
    assert login.status_code == 200

    forbidden = anonymous_client.post(
        '/api/v1/schedules',
        json={
            'name': 'Viewer schedule',
            'schedule_type': 'manual',
            'target_type': 'rule',
            'target_id': 1,
            'is_enabled': True,
        },
    )
    assert forbidden.status_code == 403


def test_invalid_cron_expression_rejected(client: TestClient):
    rule_id = create_rule(client, 'Cron rule')
    response = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Bad cron',
            'schedule_type': 'cron',
            'cron_expr': 'not a cron',
            'target_type': 'rule',
            'target_id': rule_id,
            'is_enabled': True,
        },
    )
    assert response.status_code == 422


def test_delete_schedule(client: TestClient):
    rule_id = create_rule(client, 'Delete rule')
    schedule_id = client.post(
        '/api/v1/schedules',
        json={
            'name': 'Delete me',
            'schedule_type': 'manual',
            'target_type': 'rule',
            'target_id': rule_id,
            'is_enabled': True,
        },
    ).json()['id']

    delete_response = client.delete(f'/api/v1/schedules/{schedule_id}')
    assert delete_response.status_code == 204

    get_response = client.get(f'/api/v1/schedules/{schedule_id}')
    assert get_response.status_code == 404
