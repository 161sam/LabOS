"""itops infraops v1

Revision ID: 20260420_0022
Revises: 20260420_0021
Create Date: 2026-04-20 16:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260420_0022'
down_revision: str | None = '20260420_0021'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'infranode',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('node_id', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('node_type', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='nominal'),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='general'),
        sa.Column('hostname', sa.String(length=160), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('zone', sa.String(length=120), nullable=True),
        sa.Column('location', sa.String(length=160), nullable=True),
        sa.Column('os_family', sa.String(length=60), nullable=True),
        sa.Column('architecture', sa.String(length=40), nullable=True),
        sa.Column('has_gpu', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('ros_enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('mqtt_enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('asset.id'), nullable=True),
        sa.Column(
            'autonomous_module_id',
            sa.Integer(),
            sa.ForeignKey('autonomousmodule.id'),
            nullable=True,
        ),
        sa.Column('wiki_ref', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_infranode_name', 'infranode', ['name'])
    op.create_index('ix_infranode_node_id', 'infranode', ['node_id'], unique=True)
    op.create_index('ix_infranode_node_type', 'infranode', ['node_type'])
    op.create_index('ix_infranode_status', 'infranode', ['status'])
    op.create_index('ix_infranode_role', 'infranode', ['role'])
    op.create_index('ix_infranode_zone', 'infranode', ['zone'])
    op.create_index('ix_infranode_asset_id', 'infranode', ['asset_id'])
    op.create_index('ix_infranode_autonomous_module_id', 'infranode', ['autonomous_module_id'])

    op.create_table(
        'infraservice',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('infra_node_id', sa.Integer(), sa.ForeignKey('infranode.id'), nullable=False),
        sa.Column('service_name', sa.String(length=120), nullable=False),
        sa.Column('service_type', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='nominal'),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('healthcheck_url', sa.String(length=255), nullable=True),
        sa.Column('version', sa.String(length=60), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_infraservice_infra_node_id', 'infraservice', ['infra_node_id'])
    op.create_index('ix_infraservice_service_type', 'infraservice', ['service_type'])
    op.create_index('ix_infraservice_status', 'infraservice', ['status'])
    op.create_index(
        'ix_infraservice_node_service',
        'infraservice',
        ['infra_node_id', 'service_name'],
        unique=True,
    )

    op.create_table(
        'storagevolume',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('infra_node_id', sa.Integer(), sa.ForeignKey('infranode.id'), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('mount_path', sa.String(length=255), nullable=True),
        sa.Column('volume_type', sa.String(length=40), nullable=False, server_default='local'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='nominal'),
        sa.Column('capacity_gb', sa.Float(), nullable=True),
        sa.Column('free_gb', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_storagevolume_infra_node_id', 'storagevolume', ['infra_node_id'])
    op.create_index('ix_storagevolume_status', 'storagevolume', ['status'])
    op.create_index('ix_storagevolume_volume_type', 'storagevolume', ['volume_type'])

    op.create_table(
        'backuprecord',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('infra_node_id', sa.Integer(), sa.ForeignKey('infranode.id'), nullable=True),
        sa.Column('target_type', sa.String(length=40), nullable=True),
        sa.Column('target_id', sa.String(length=120), nullable=True),
        sa.Column('backup_type', sa.String(length=40), nullable=False, server_default='snapshot'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='ok'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_backuprecord_infra_node_id', 'backuprecord', ['infra_node_id'])
    op.create_index('ix_backuprecord_status', 'backuprecord', ['status'])
    op.create_index('ix_backuprecord_backup_type', 'backuprecord', ['backup_type'])
    op.create_index('ix_backuprecord_started_at', 'backuprecord', ['started_at'])


def downgrade() -> None:
    op.drop_index('ix_backuprecord_started_at', table_name='backuprecord')
    op.drop_index('ix_backuprecord_backup_type', table_name='backuprecord')
    op.drop_index('ix_backuprecord_status', table_name='backuprecord')
    op.drop_index('ix_backuprecord_infra_node_id', table_name='backuprecord')
    op.drop_table('backuprecord')

    op.drop_index('ix_storagevolume_volume_type', table_name='storagevolume')
    op.drop_index('ix_storagevolume_status', table_name='storagevolume')
    op.drop_index('ix_storagevolume_infra_node_id', table_name='storagevolume')
    op.drop_table('storagevolume')

    op.drop_index('ix_infraservice_node_service', table_name='infraservice')
    op.drop_index('ix_infraservice_status', table_name='infraservice')
    op.drop_index('ix_infraservice_service_type', table_name='infraservice')
    op.drop_index('ix_infraservice_infra_node_id', table_name='infraservice')
    op.drop_table('infraservice')

    op.drop_index('ix_infranode_autonomous_module_id', table_name='infranode')
    op.drop_index('ix_infranode_asset_id', table_name='infranode')
    op.drop_index('ix_infranode_zone', table_name='infranode')
    op.drop_index('ix_infranode_role', table_name='infranode')
    op.drop_index('ix_infranode_status', table_name='infranode')
    op.drop_index('ix_infranode_node_type', table_name='infranode')
    op.drop_index('ix_infranode_node_id', table_name='infranode')
    op.drop_index('ix_infranode_name', table_name='infranode')
    op.drop_table('infranode')
