"""add photo storage metadata for visual documentation v1

Revision ID: 20260417_0004
Revises: 20260417_0003
Create Date: 2026-04-17 18:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260417_0004'
down_revision: Union[str, None] = '20260417_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('charge_id', sa.Integer(), nullable=True),
        sa.Column('reactor_id', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
        sa.Column('uploaded_by', sa.String(), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('photo') as batch_op:
        batch_op.create_index('ix_photo_created_at', ['created_at'], unique=False)
        batch_op.create_index('ix_photo_charge_id', ['charge_id'], unique=False)
        batch_op.create_index('ix_photo_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_photo_captured_at', ['captured_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('photo') as batch_op:
        batch_op.drop_index('ix_photo_captured_at')
        batch_op.drop_index('ix_photo_reactor_id')
        batch_op.drop_index('ix_photo_charge_id')
        batch_op.drop_index('ix_photo_created_at')
    op.drop_table('photo')
