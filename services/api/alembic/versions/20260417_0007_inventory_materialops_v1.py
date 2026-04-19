"""add inventory and materialops v1

Revision ID: 20260417_0007
Revises: 20260417_0006
Create Date: 2026-04-17 23:45:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260417_0007'
down_revision: Union[str, None] = '20260417_0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'inventoryitem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='available'),
        sa.Column('quantity', sa.Numeric(12, 3), nullable=False, server_default='0'),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('min_quantity', sa.Numeric(12, 3), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('zone', sa.String(), nullable=True),
        sa.Column('supplier', sa.String(), nullable=True),
        sa.Column('sku', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('asset_id', sa.Integer(), nullable=True),
        sa.Column('wiki_ref', sa.String(), nullable=True),
        sa.Column('last_restocked_at', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('inventoryitem') as batch_op:
        batch_op.create_index('ix_inventoryitem_name', ['name'], unique=False)
        batch_op.create_index('ix_inventoryitem_category', ['category'], unique=False)
        batch_op.create_index('ix_inventoryitem_status', ['status'], unique=False)
        batch_op.create_index('ix_inventoryitem_location', ['location'], unique=False)
        batch_op.create_index('ix_inventoryitem_zone', ['zone'], unique=False)
        batch_op.create_index('ix_inventoryitem_asset_id', ['asset_id'], unique=False)
        batch_op.create_index('ix_inventoryitem_sku', ['sku'], unique=False)
        batch_op.create_index('ix_inventoryitem_expiry_date', ['expiry_date'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('inventoryitem') as batch_op:
        batch_op.drop_index('ix_inventoryitem_expiry_date')
        batch_op.drop_index('ix_inventoryitem_sku')
        batch_op.drop_index('ix_inventoryitem_asset_id')
        batch_op.drop_index('ix_inventoryitem_zone')
        batch_op.drop_index('ix_inventoryitem_location')
        batch_op.drop_index('ix_inventoryitem_status')
        batch_op.drop_index('ix_inventoryitem_category')
        batch_op.drop_index('ix_inventoryitem_name')

    op.drop_table('inventoryitem')
