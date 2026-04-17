"""baseline schema for bootstrap and core CRUD modules

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 14:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260417_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names(inspector: sa.Inspector) -> set[str]:
    return set(inspector.get_table_names())


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column['name'] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index['name'] for index in inspector.get_indexes(table_name)}


def _create_charge_table() -> None:
    op.create_table(
        'charge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('species', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('volume_l', sa.Float(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_reactor_table() -> None:
    op.create_table(
        'reactor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('reactor_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('volume_l', sa.Float(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('last_cleaned_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_sensor_table() -> None:
    op.create_table(
        'sensor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sensor_type', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_sensor_value_table() -> None:
    op.create_table(
        'sensorvalue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sensor_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_task_table() -> None:
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_alert_table() -> None:
    op.create_table(
        'alert',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def _create_wiki_page_table() -> None:
    op.create_table(
        'wikipage',
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('slug'),
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = _table_names(inspector)

    if 'charge' not in table_names:
        _create_charge_table()
    if 'reactor' not in table_names:
        _create_reactor_table()
    if 'sensor' not in table_names:
        _create_sensor_table()
    if 'sensorvalue' not in table_names:
        _create_sensor_value_table()
    if 'task' not in table_names:
        _create_task_table()
    if 'alert' not in table_names:
        _create_alert_table()
    if 'wikipage' not in table_names:
        _create_wiki_page_table()

    inspector = sa.inspect(bind)
    reactor_columns = _column_names(inspector, 'reactor')
    if 'last_cleaned_at' not in reactor_columns:
        op.add_column('reactor', sa.Column('last_cleaned_at', sa.DateTime(), nullable=True))
    if 'notes' not in reactor_columns:
        op.add_column('reactor', sa.Column('notes', sa.String(), nullable=True))

    charge_indexes = _index_names(inspector, 'charge')
    if 'ix_charge_name' not in charge_indexes:
        op.create_index('ix_charge_name', 'charge', ['name'], unique=False)
    if 'ix_charge_status' not in charge_indexes:
        op.create_index('ix_charge_status', 'charge', ['status'], unique=False)
    if 'ix_charge_reactor_id' not in charge_indexes:
        op.create_index('ix_charge_reactor_id', 'charge', ['reactor_id'], unique=False)
    if 'ix_charge_start_date' not in charge_indexes:
        op.create_index('ix_charge_start_date', 'charge', ['start_date'], unique=False)

    reactor_indexes = _index_names(inspector, 'reactor')
    if 'ix_reactor_name' not in reactor_indexes:
        op.create_index('ix_reactor_name', 'reactor', ['name'], unique=False)
    if 'ix_reactor_status' not in reactor_indexes:
        op.create_index('ix_reactor_status', 'reactor', ['status'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = _table_names(inspector)

    if 'charge' in table_names:
        charge_indexes = _index_names(inspector, 'charge')
        if 'ix_charge_start_date' in charge_indexes:
            op.drop_index('ix_charge_start_date', table_name='charge')
        if 'ix_charge_reactor_id' in charge_indexes:
            op.drop_index('ix_charge_reactor_id', table_name='charge')
        if 'ix_charge_status' in charge_indexes:
            op.drop_index('ix_charge_status', table_name='charge')
        if 'ix_charge_name' in charge_indexes:
            op.drop_index('ix_charge_name', table_name='charge')

    if 'reactor' in table_names:
        reactor_indexes = _index_names(inspector, 'reactor')
        if 'ix_reactor_status' in reactor_indexes:
            op.drop_index('ix_reactor_status', table_name='reactor')
        if 'ix_reactor_name' in reactor_indexes:
            op.drop_index('ix_reactor_name', table_name='reactor')

    inspector = sa.inspect(bind)
    table_names = _table_names(inspector)

    if 'wikipage' in table_names:
        op.drop_table('wikipage')
    if 'alert' in table_names:
        op.drop_table('alert')
    if 'task' in table_names:
        op.drop_table('task')
    if 'sensorvalue' in table_names:
        op.drop_table('sensorvalue')
    if 'sensor' in table_names:
        op.drop_table('sensor')
    if 'reactor' in table_names:
        op.drop_table('reactor')
    if 'charge' in table_names:
        op.drop_table('charge')
