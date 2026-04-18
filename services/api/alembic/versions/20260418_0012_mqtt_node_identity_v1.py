"""mqtt node identity v1

Revision ID: 20260418_0012
Revises: 20260418_0011
Create Date: 2026-04-18 14:20:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260418_0012'
down_revision: str | None = '20260418_0011'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('devicenode', sa.Column('node_id', sa.String(length=120), nullable=True))
    op.create_index('ix_devicenode_node_id', 'devicenode', ['node_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_devicenode_node_id', table_name='devicenode')
    op.drop_column('devicenode', 'node_id')
