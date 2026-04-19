"""abrain execution log v1

Revision ID: 20260419_0018
Revises: 20260419_0017
Create Date: 2026-04-19 17:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0018'
down_revision: str | None = '20260419_0017'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'abrainexecutionlog',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('params', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('blocked_reason', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('executed_by', sa.String(), nullable=True),
        sa.Column('trace_id', sa.String(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_abrainexecutionlog_action', 'abrainexecutionlog', ['action'])
    op.create_index('ix_abrainexecutionlog_status', 'abrainexecutionlog', ['status'])
    op.create_index('ix_abrainexecutionlog_trace_id', 'abrainexecutionlog', ['trace_id'])
    op.create_index('ix_abrainexecutionlog_created_at', 'abrainexecutionlog', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_abrainexecutionlog_created_at', table_name='abrainexecutionlog')
    op.drop_index('ix_abrainexecutionlog_trace_id', table_name='abrainexecutionlog')
    op.drop_index('ix_abrainexecutionlog_status', table_name='abrainexecutionlog')
    op.drop_index('ix_abrainexecutionlog_action', table_name='abrainexecutionlog')
    op.drop_table('abrainexecutionlog')
