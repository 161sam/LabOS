"""add assets and device references for assetops v1

Revision ID: 20260417_0006
Revises: 20260417_0005
Create Date: 2026-04-17 23:10:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260417_0006'
down_revision: Union[str, None] = '20260417_0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'asset',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('asset_type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('zone', sa.String(), nullable=True),
        sa.Column('serial_number', sa.String(), nullable=True),
        sa.Column('manufacturer', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('maintenance_notes', sa.String(), nullable=True),
        sa.Column('last_maintenance_at', sa.DateTime(), nullable=True),
        sa.Column('next_maintenance_at', sa.DateTime(), nullable=True),
        sa.Column('wiki_ref', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('asset') as batch_op:
        batch_op.create_index('ix_asset_name', ['name'], unique=False)
        batch_op.create_index('ix_asset_status', ['status'], unique=False)
        batch_op.create_index('ix_asset_asset_type', ['asset_type'], unique=False)
        batch_op.create_index('ix_asset_category', ['category'], unique=False)
        batch_op.create_index('ix_asset_location', ['location'], unique=False)
        batch_op.create_index('ix_asset_zone', ['zone'], unique=False)
        batch_op.create_index('ix_asset_next_maintenance_at', ['next_maintenance_at'], unique=False)

    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('asset_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_task_asset_id', ['asset_id'], unique=False)

    with op.batch_alter_table('photo') as batch_op:
        batch_op.add_column(sa.Column('asset_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_photo_asset_id', ['asset_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('photo') as batch_op:
        batch_op.drop_index('ix_photo_asset_id')
        batch_op.drop_column('asset_id')

    with op.batch_alter_table('task') as batch_op:
        batch_op.drop_index('ix_task_asset_id')
        batch_op.drop_column('asset_id')

    with op.batch_alter_table('asset') as batch_op:
        batch_op.drop_index('ix_asset_next_maintenance_at')
        batch_op.drop_index('ix_asset_zone')
        batch_op.drop_index('ix_asset_location')
        batch_op.drop_index('ix_asset_category')
        batch_op.drop_index('ix_asset_asset_type')
        batch_op.drop_index('ix_asset_status')
        batch_op.drop_index('ix_asset_name')

    op.drop_table('asset')
