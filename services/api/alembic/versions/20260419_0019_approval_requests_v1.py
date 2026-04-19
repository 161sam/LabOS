"""approval requests v1

Revision ID: 20260419_0019
Revises: 20260419_0018
Create Date: 2026-04-19 18:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0019'
down_revision: str | None = '20260419_0018'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'approvalrequest',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('action_name', sa.String(), nullable=False),
        sa.Column('action_params', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('requested_by_source', sa.String(), nullable=False),
        sa.Column('requested_by_user_id', sa.Integer(), sa.ForeignKey('useraccount.id'), nullable=True),
        sa.Column('requested_via', sa.String(), nullable=False),
        sa.Column('trace_id', sa.String(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('decision_note', sa.String(), nullable=True),
        sa.Column('approval_required', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('approved_by_user_id', sa.Integer(), sa.ForeignKey('useraccount.id'), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.Column('executed_execution_log_id', sa.Integer(), sa.ForeignKey('abrainexecutionlog.id'), nullable=True),
        sa.Column('blocked_reason', sa.String(), nullable=True),
        sa.Column('last_error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_approvalrequest_status', 'approvalrequest', ['status'])
    op.create_index('ix_approvalrequest_action_name', 'approvalrequest', ['action_name'])
    op.create_index('ix_approvalrequest_trace_id', 'approvalrequest', ['trace_id'])
    op.create_index('ix_approvalrequest_requested_by_source', 'approvalrequest', ['requested_by_source'])
    op.create_index('ix_approvalrequest_created_at', 'approvalrequest', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_approvalrequest_created_at', table_name='approvalrequest')
    op.drop_index('ix_approvalrequest_requested_by_source', table_name='approvalrequest')
    op.drop_index('ix_approvalrequest_trace_id', table_name='approvalrequest')
    op.drop_index('ix_approvalrequest_action_name', table_name='approvalrequest')
    op.drop_index('ix_approvalrequest_status', table_name='approvalrequest')
    op.drop_table('approvalrequest')
