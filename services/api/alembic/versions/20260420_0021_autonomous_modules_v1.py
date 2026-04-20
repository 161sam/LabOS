"""autonomous modules v1

Revision ID: 20260420_0021
Revises: 20260419_0020
Create Date: 2026-04-20 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260420_0021'
down_revision: str | None = '20260419_0020'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'autonomousmodule',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_id', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('module_type', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='nominal'),
        sa.Column('autonomy_level', sa.String(length=30), nullable=False, server_default='manual'),
        sa.Column('reactor_id', sa.Integer(), sa.ForeignKey('reactor.id'), nullable=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('asset.id'), nullable=True),
        sa.Column('device_node_id', sa.Integer(), sa.ForeignKey('devicenode.id'), nullable=True),
        sa.Column('zone', sa.String(length=120), nullable=True),
        sa.Column('location', sa.String(length=160), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('ros_node_name', sa.String(length=160), nullable=True),
        sa.Column('mqtt_node_id', sa.String(length=120), nullable=True),
        sa.Column('wiki_ref', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_autonomousmodule_module_id', 'autonomousmodule', ['module_id'], unique=True)
    op.create_index('ix_autonomousmodule_module_type', 'autonomousmodule', ['module_type'])
    op.create_index('ix_autonomousmodule_status', 'autonomousmodule', ['status'])
    op.create_index('ix_autonomousmodule_autonomy_level', 'autonomousmodule', ['autonomy_level'])
    op.create_index('ix_autonomousmodule_reactor_id', 'autonomousmodule', ['reactor_id'])
    op.create_index('ix_autonomousmodule_asset_id', 'autonomousmodule', ['asset_id'])
    op.create_index('ix_autonomousmodule_device_node_id', 'autonomousmodule', ['device_node_id'])
    op.create_index('ix_autonomousmodule_zone', 'autonomousmodule', ['zone'])
    op.create_index('ix_autonomousmodule_name', 'autonomousmodule', ['name'])

    op.create_table(
        'modulecapability',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('autonomous_module_id', sa.Integer(), sa.ForeignKey('autonomousmodule.id'), nullable=False),
        sa.Column('capability_type', sa.String(length=60), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index(
        'ix_modulecapability_module_capability',
        'modulecapability',
        ['autonomous_module_id', 'capability_type'],
        unique=True,
    )
    op.create_index('ix_modulecapability_autonomous_module_id', 'modulecapability', ['autonomous_module_id'])
    op.create_index('ix_modulecapability_capability_type', 'modulecapability', ['capability_type'])


def downgrade() -> None:
    op.drop_index('ix_modulecapability_capability_type', table_name='modulecapability')
    op.drop_index('ix_modulecapability_autonomous_module_id', table_name='modulecapability')
    op.drop_index('ix_modulecapability_module_capability', table_name='modulecapability')
    op.drop_table('modulecapability')
    op.drop_index('ix_autonomousmodule_name', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_zone', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_device_node_id', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_asset_id', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_reactor_id', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_autonomy_level', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_status', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_module_type', table_name='autonomousmodule')
    op.drop_index('ix_autonomousmodule_module_id', table_name='autonomousmodule')
    op.drop_table('autonomousmodule')
