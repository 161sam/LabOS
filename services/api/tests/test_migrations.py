from sqlalchemy import create_engine, inspect, text

from app.db import get_alembic_config


def test_alembic_upgrade_applies_baseline_schema(tmp_path):
    db_path = tmp_path / 'migration-check.db'
    database_url = f'sqlite:///{db_path}'

    from alembic import command

    command.upgrade(get_alembic_config(database_url), 'head')

    engine = create_engine(database_url, connect_args={'check_same_thread': False})
    inspector = inspect(engine)

    table_names = set(inspector.get_table_names())
    assert {'charge', 'reactor', 'sensor', 'sensorvalue', 'task', 'alert', 'wikipage'} <= table_names

    charge_columns = {column['name'] for column in inspector.get_columns('charge')}
    assert {'id', 'name', 'species', 'status', 'volume_l', 'reactor_id', 'start_date', 'notes'} <= charge_columns

    reactor_columns = {column['name'] for column in inspector.get_columns('reactor')}
    assert {'id', 'name', 'reactor_type', 'status', 'volume_l', 'location', 'last_cleaned_at', 'notes'} <= reactor_columns

    sensor_columns = {column['name'] for column in inspector.get_columns('sensor')}
    assert {
        'id',
        'name',
        'sensor_type',
        'unit',
        'reactor_id',
        'status',
        'location',
        'notes',
        'created_at',
        'updated_at',
    } <= sensor_columns

    sensor_value_columns = {column['name'] for column in inspector.get_columns('sensorvalue')}
    assert {'id', 'sensor_id', 'value', 'recorded_at', 'source'} <= sensor_value_columns

    task_columns = {column['name'] for column in inspector.get_columns('task')}
    assert {
        'id',
        'title',
        'description',
        'status',
        'priority',
        'due_at',
        'charge_id',
        'reactor_id',
        'created_at',
        'updated_at',
        'completed_at',
    } <= task_columns

    alert_columns = {column['name'] for column in inspector.get_columns('alert')}
    assert {
        'id',
        'title',
        'message',
        'severity',
        'status',
        'source_type',
        'source_id',
        'created_at',
        'acknowledged_at',
        'resolved_at',
    } <= alert_columns

    charge_indexes = {index['name'] for index in inspector.get_indexes('charge')}
    assert {'ix_charge_name', 'ix_charge_status', 'ix_charge_reactor_id', 'ix_charge_start_date'} <= charge_indexes

    reactor_indexes = {index['name'] for index in inspector.get_indexes('reactor')}
    assert {'ix_reactor_name', 'ix_reactor_status'} <= reactor_indexes

    sensor_indexes = {index['name'] for index in inspector.get_indexes('sensor')}
    assert {'ix_sensor_name', 'ix_sensor_status', 'ix_sensor_sensor_type', 'ix_sensor_reactor_id'} <= sensor_indexes

    sensor_value_indexes = {index['name'] for index in inspector.get_indexes('sensorvalue')}
    assert {
        'ix_sensorvalue_sensor_id',
        'ix_sensorvalue_recorded_at',
        'ix_sensorvalue_sensor_id_recorded_at',
    } <= sensor_value_indexes

    task_indexes = {index['name'] for index in inspector.get_indexes('task')}
    assert {
        'ix_task_status',
        'ix_task_priority',
        'ix_task_due_at',
        'ix_task_charge_id',
        'ix_task_reactor_id',
    } <= task_indexes

    alert_indexes = {index['name'] for index in inspector.get_indexes('alert')}
    assert {
        'ix_alert_severity',
        'ix_alert_status',
        'ix_alert_source_type',
        'ix_alert_created_at',
    } <= alert_indexes

    with engine.connect() as connection:
        version = connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one()
        assert version == '20260417_0003'

    engine.dispose()
