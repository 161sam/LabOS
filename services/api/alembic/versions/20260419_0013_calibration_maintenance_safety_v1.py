"""calibration maintenance safety v1

Revision ID: 20260419_0013
Revises: 20260418_0012
Create Date: 2026-04-19 08:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0013'
down_revision: str | None = '20260418_0012'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('reactorcommand', sa.Column('blocked_reason', sa.String(), nullable=True))

    op.create_table(
        'calibrationrecord',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('parameter', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='unknown'),
        sa.Column('calibrated_at', sa.DateTime(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('calibration_value', sa.Float(), nullable=True),
        sa.Column('reference_value', sa.Float(), nullable=True),
        sa.Column('performed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['useraccount.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_calibrationrecord_target_type_target_id', 'calibrationrecord', ['target_type', 'target_id'])
    op.create_index('ix_calibrationrecord_status', 'calibrationrecord', ['status'])
    op.create_index('ix_calibrationrecord_due_at', 'calibrationrecord', ['due_at'])
    op.create_index('ix_calibrationrecord_created_at', 'calibrationrecord', ['created_at'])

    op.create_table(
        'maintenancerecord',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='scheduled'),
        sa.Column('performed_at', sa.DateTime(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('performed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['useraccount.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_maintenancerecord_target_type_target_id', 'maintenancerecord', ['target_type', 'target_id'])
    op.create_index('ix_maintenancerecord_status', 'maintenancerecord', ['status'])
    op.create_index('ix_maintenancerecord_due_at', 'maintenancerecord', ['due_at'])
    op.create_index('ix_maintenancerecord_created_at', 'maintenancerecord', ['created_at'])

    op.create_table(
        'safetyincident',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=True),
        sa.Column('device_node_id', sa.Integer(), nullable=True),
        sa.Column('asset_id', sa.Integer(), nullable=True),
        sa.Column('incident_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, server_default='warning'),
        sa.Column('status', sa.String(), nullable=False, server_default='open'),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.ForeignKeyConstraint(['device_node_id'], ['devicenode.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['useraccount.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_safetyincident_reactor_id', 'safetyincident', ['reactor_id'])
    op.create_index('ix_safetyincident_device_node_id', 'safetyincident', ['device_node_id'])
    op.create_index('ix_safetyincident_status', 'safetyincident', ['status'])
    op.create_index('ix_safetyincident_severity', 'safetyincident', ['severity'])
    op.create_index('ix_safetyincident_incident_type', 'safetyincident', ['incident_type'])
    op.create_index('ix_safetyincident_created_at', 'safetyincident', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_safetyincident_created_at', table_name='safetyincident')
    op.drop_index('ix_safetyincident_incident_type', table_name='safetyincident')
    op.drop_index('ix_safetyincident_severity', table_name='safetyincident')
    op.drop_index('ix_safetyincident_status', table_name='safetyincident')
    op.drop_index('ix_safetyincident_device_node_id', table_name='safetyincident')
    op.drop_index('ix_safetyincident_reactor_id', table_name='safetyincident')
    op.drop_table('safetyincident')

    op.drop_index('ix_maintenancerecord_created_at', table_name='maintenancerecord')
    op.drop_index('ix_maintenancerecord_due_at', table_name='maintenancerecord')
    op.drop_index('ix_maintenancerecord_status', table_name='maintenancerecord')
    op.drop_index('ix_maintenancerecord_target_type_target_id', table_name='maintenancerecord')
    op.drop_table('maintenancerecord')

    op.drop_index('ix_calibrationrecord_created_at', table_name='calibrationrecord')
    op.drop_index('ix_calibrationrecord_due_at', table_name='calibrationrecord')
    op.drop_index('ix_calibrationrecord_status', table_name='calibrationrecord')
    op.drop_index('ix_calibrationrecord_target_type_target_id', table_name='calibrationrecord')
    op.drop_table('calibrationrecord')

    op.drop_column('reactorcommand', 'blocked_reason')
