"""add reactor control telemetry v1

Revision ID: 20260418_0011
Revises: 20260418_0010
Create Date: 2026-04-18 19:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260418_0011'
down_revision: Union[str, None] = '20260418_0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'telemetryvalue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('sensor_type', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False, server_default='manual'),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('telemetryvalue') as batch_op:
        batch_op.create_index('ix_telemetryvalue_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_telemetryvalue_reactor_id_timestamp', ['reactor_id', 'timestamp'], unique=False)
        batch_op.create_index('ix_telemetryvalue_sensor_type', ['sensor_type'], unique=False)
        batch_op.create_index('ix_telemetryvalue_timestamp', ['timestamp'], unique=False)

    op.create_table(
        'devicenode',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('node_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='online'),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('firmware_version', sa.String(), nullable=True),
        sa.Column('reactor_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('devicenode') as batch_op:
        batch_op.create_index('ix_devicenode_name', ['name'], unique=False)
        batch_op.create_index('ix_devicenode_node_type', ['node_type'], unique=False)
        batch_op.create_index('ix_devicenode_status', ['status'], unique=False)
        batch_op.create_index('ix_devicenode_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_devicenode_last_seen_at', ['last_seen_at'], unique=False)

    op.create_table(
        'reactorsetpoint',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('parameter', sa.String(), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('mode', sa.String(), nullable=False, server_default='manual'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('reactorsetpoint') as batch_op:
        batch_op.create_index('ix_reactorsetpoint_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_reactorsetpoint_reactor_id_parameter', ['reactor_id', 'parameter'], unique=False)
        batch_op.create_index('ix_reactorsetpoint_parameter', ['parameter'], unique=False)
        batch_op.create_index('ix_reactorsetpoint_mode', ['mode'], unique=False)

    op.create_table(
        'reactorcommand',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('command_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('reactorcommand') as batch_op:
        batch_op.create_index('ix_reactorcommand_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_reactorcommand_reactor_id_created_at', ['reactor_id', 'created_at'], unique=False)
        batch_op.create_index('ix_reactorcommand_status', ['status'], unique=False)
        batch_op.create_index('ix_reactorcommand_command_type', ['command_type'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('reactorcommand') as batch_op:
        batch_op.drop_index('ix_reactorcommand_command_type')
        batch_op.drop_index('ix_reactorcommand_status')
        batch_op.drop_index('ix_reactorcommand_reactor_id_created_at')
        batch_op.drop_index('ix_reactorcommand_reactor_id')
    op.drop_table('reactorcommand')

    with op.batch_alter_table('reactorsetpoint') as batch_op:
        batch_op.drop_index('ix_reactorsetpoint_mode')
        batch_op.drop_index('ix_reactorsetpoint_parameter')
        batch_op.drop_index('ix_reactorsetpoint_reactor_id_parameter')
        batch_op.drop_index('ix_reactorsetpoint_reactor_id')
    op.drop_table('reactorsetpoint')

    with op.batch_alter_table('devicenode') as batch_op:
        batch_op.drop_index('ix_devicenode_last_seen_at')
        batch_op.drop_index('ix_devicenode_reactor_id')
        batch_op.drop_index('ix_devicenode_status')
        batch_op.drop_index('ix_devicenode_node_type')
        batch_op.drop_index('ix_devicenode_name')
    op.drop_table('devicenode')

    with op.batch_alter_table('telemetryvalue') as batch_op:
        batch_op.drop_index('ix_telemetryvalue_timestamp')
        batch_op.drop_index('ix_telemetryvalue_sensor_type')
        batch_op.drop_index('ix_telemetryvalue_reactor_id_timestamp')
        batch_op.drop_index('ix_telemetryvalue_reactor_id')
    op.drop_table('telemetryvalue')
