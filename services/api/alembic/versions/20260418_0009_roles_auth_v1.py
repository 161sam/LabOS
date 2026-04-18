"""add roles auth v1

Revision ID: 20260418_0009
Revises: 20260418_0008
Create Date: 2026-04-18 12:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260418_0009'
down_revision: Union[str, None] = '20260418_0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'useraccount',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='viewer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('auth_source', sa.String(), nullable=False, server_default='local'),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='uq_useraccount_username'),
    )
    with op.batch_alter_table('useraccount') as batch_op:
        batch_op.create_index('ix_useraccount_username', ['username'], unique=False)
        batch_op.create_index('ix_useraccount_role', ['role'], unique=False)
        batch_op.create_index('ix_useraccount_is_active', ['is_active'], unique=False)
        batch_op.create_index('ix_useraccount_email', ['email'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('useraccount') as batch_op:
        batch_op.drop_index('ix_useraccount_email')
        batch_op.drop_index('ix_useraccount_is_active')
        batch_op.drop_index('ix_useraccount_role')
        batch_op.drop_index('ix_useraccount_username')

    op.drop_table('useraccount')
