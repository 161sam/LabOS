"""trace context v1

Revision ID: 20260419_0020
Revises: 20260419_0019
Create Date: 2026-04-19 19:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0020'
down_revision: str | None = '20260419_0019'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'tracecontext',
        sa.Column('trace_id', sa.String(), primary_key=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='open'),
        sa.Column('root_query', sa.String(), nullable=True),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('context_snapshot', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_tracecontext_status', 'tracecontext', ['status'])
    op.create_index('ix_tracecontext_source', 'tracecontext', ['source'])
    op.create_index('ix_tracecontext_created_at', 'tracecontext', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_tracecontext_created_at', table_name='tracecontext')
    op.drop_index('ix_tracecontext_source', table_name='tracecontext')
    op.drop_index('ix_tracecontext_status', table_name='tracecontext')
    op.drop_table('tracecontext')
