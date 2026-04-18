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
    assert {
        'charge',
        'reactor',
        'sensor',
        'sensorvalue',
        'task',
        'alert',
        'photo',
        'asset',
        'inventoryitem',
        'label',
        'rule',
        'ruleexecution',
        'useraccount',
        'wikipage',
    } <= table_names

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
        'asset_id',
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

    photo_columns = {column['name'] for column in inspector.get_columns('photo')}
    assert {
        'id',
        'filename',
        'original_filename',
        'mime_type',
        'size_bytes',
        'storage_path',
        'title',
        'notes',
        'charge_id',
        'reactor_id',
        'asset_id',
        'created_at',
        'uploaded_by',
        'captured_at',
    } <= photo_columns

    asset_columns = {column['name'] for column in inspector.get_columns('asset')}
    assert {
        'id',
        'name',
        'asset_type',
        'category',
        'status',
        'location',
        'zone',
        'serial_number',
        'manufacturer',
        'model',
        'notes',
        'maintenance_notes',
        'last_maintenance_at',
        'next_maintenance_at',
        'wiki_ref',
        'created_at',
        'updated_at',
    } <= asset_columns

    inventory_columns = {column['name'] for column in inspector.get_columns('inventoryitem')}
    assert {
        'id',
        'name',
        'category',
        'status',
        'quantity',
        'unit',
        'min_quantity',
        'location',
        'zone',
        'supplier',
        'sku',
        'notes',
        'asset_id',
        'wiki_ref',
        'last_restocked_at',
        'expiry_date',
        'created_at',
        'updated_at',
    } <= inventory_columns

    label_columns = {column['name'] for column in inspector.get_columns('label')}
    assert {
        'id',
        'label_code',
        'label_type',
        'target_type',
        'target_id',
        'display_name',
        'location_snapshot',
        'note',
        'is_active',
        'created_at',
        'updated_at',
    } <= label_columns

    rule_columns = {column['name'] for column in inspector.get_columns('rule')}
    assert {
        'id',
        'name',
        'description',
        'is_enabled',
        'trigger_type',
        'condition_type',
        'condition_config',
        'action_type',
        'action_config',
        'created_at',
        'updated_at',
        'last_evaluated_at',
    } <= rule_columns

    rule_execution_columns = {column['name'] for column in inspector.get_columns('ruleexecution')}
    assert {
        'id',
        'rule_id',
        'status',
        'dry_run',
        'evaluation_summary',
        'action_result',
        'created_at',
    } <= rule_execution_columns

    user_columns = {column['name'] for column in inspector.get_columns('useraccount')}
    assert {
        'id',
        'username',
        'display_name',
        'email',
        'password_hash',
        'role',
        'is_active',
        'auth_source',
        'note',
        'created_at',
        'updated_at',
        'last_login_at',
    } <= user_columns

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
        'ix_task_asset_id',
    } <= task_indexes

    alert_indexes = {index['name'] for index in inspector.get_indexes('alert')}
    assert {
        'ix_alert_severity',
        'ix_alert_status',
        'ix_alert_source_type',
        'ix_alert_created_at',
    } <= alert_indexes

    photo_indexes = {index['name'] for index in inspector.get_indexes('photo')}
    assert {
        'ix_photo_created_at',
        'ix_photo_charge_id',
        'ix_photo_reactor_id',
        'ix_photo_asset_id',
        'ix_photo_captured_at',
    } <= photo_indexes

    asset_indexes = {index['name'] for index in inspector.get_indexes('asset')}
    assert {
        'ix_asset_name',
        'ix_asset_status',
        'ix_asset_asset_type',
        'ix_asset_category',
        'ix_asset_location',
        'ix_asset_zone',
        'ix_asset_next_maintenance_at',
    } <= asset_indexes

    inventory_indexes = {index['name'] for index in inspector.get_indexes('inventoryitem')}
    assert {
        'ix_inventoryitem_name',
        'ix_inventoryitem_category',
        'ix_inventoryitem_status',
        'ix_inventoryitem_location',
        'ix_inventoryitem_zone',
        'ix_inventoryitem_asset_id',
        'ix_inventoryitem_sku',
        'ix_inventoryitem_expiry_date',
    } <= inventory_indexes

    label_indexes = {index['name'] for index in inspector.get_indexes('label')}
    assert {
        'ix_label_label_code',
        'ix_label_target_id',
        'ix_label_label_type',
        'ix_label_target_type',
        'ix_label_target_type_target_id',
        'ix_label_is_active',
        'ix_label_created_at',
    } <= label_indexes

    rule_indexes = {index['name'] for index in inspector.get_indexes('rule')}
    assert {
        'ix_rule_is_enabled',
        'ix_rule_trigger_type',
        'ix_rule_action_type',
        'ix_rule_updated_at',
    } <= rule_indexes

    rule_execution_indexes = {index['name'] for index in inspector.get_indexes('ruleexecution')}
    assert {
        'ix_ruleexecution_rule_id',
        'ix_ruleexecution_status',
        'ix_ruleexecution_created_at',
    } <= rule_execution_indexes

    user_indexes = {index['name'] for index in inspector.get_indexes('useraccount')}
    assert {
        'ix_useraccount_username',
        'ix_useraccount_role',
        'ix_useraccount_is_active',
        'ix_useraccount_email',
    } <= user_indexes

    with engine.connect() as connection:
        version = connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one()
        assert version == '20260418_0009'

    engine.dispose()
