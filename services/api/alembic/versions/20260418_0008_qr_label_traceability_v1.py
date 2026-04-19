"""add qr label traceability v1

Revision ID: 20260418_0008
Revises: 20260417_0007
Create Date: 2026-04-18 10:15:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260418_0008'
down_revision: Union[str, None] = '20260417_0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'label',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label_code', sa.String(), nullable=False),
        sa.Column('label_type', sa.String(), nullable=False, server_default='qr'),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('location_snapshot', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label_code', name='uq_label_label_code'),
    )
    with op.batch_alter_table('label') as batch_op:
        batch_op.create_index('ix_label_label_code', ['label_code'], unique=False)
        batch_op.create_index('ix_label_target_id', ['target_id'], unique=False)
        batch_op.create_index('ix_label_label_type', ['label_type'], unique=False)
        batch_op.create_index('ix_label_target_type', ['target_type'], unique=False)
        batch_op.create_index('ix_label_target_type_target_id', ['target_type', 'target_id'], unique=False)
        batch_op.create_index('ix_label_is_active', ['is_active'], unique=False)
        batch_op.create_index('ix_label_created_at', ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('label') as batch_op:
        batch_op.drop_index('ix_label_created_at')
        batch_op.drop_index('ix_label_is_active')
        batch_op.drop_index('ix_label_target_type_target_id')
        batch_op.drop_index('ix_label_target_type')
        batch_op.drop_index('ix_label_label_type')
        batch_op.drop_index('ix_label_target_id')
        batch_op.drop_index('ix_label_label_code')

    op.drop_table('label')
