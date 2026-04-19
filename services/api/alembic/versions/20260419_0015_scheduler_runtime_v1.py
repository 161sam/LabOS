"""scheduler runtime v1

Revision ID: 20260419_0015
Revises: 20260419_0014
Create Date: 2026-04-19 13:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0015'
down_revision: str | None = '20260419_0014'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'schedule',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('schedule_type', sa.String(), nullable=False),
        sa.Column('interval_seconds', sa.Integer(), nullable=True),
        sa.Column('cron_expr', sa.String(), nullable=True),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('reactor_id', sa.Integer(), sa.ForeignKey('reactor.id'), nullable=True),
        sa.Column('target_params', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('last_status', sa.String(), nullable=True),
        sa.Column('last_error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_schedule_is_enabled', 'schedule', ['is_enabled'])
    op.create_index('ix_schedule_schedule_type', 'schedule', ['schedule_type'])
    op.create_index('ix_schedule_target_type', 'schedule', ['target_type'])
    op.create_index('ix_schedule_next_run_at', 'schedule', ['next_run_at'])
    op.create_index('ix_schedule_reactor_id', 'schedule', ['reactor_id'])

    op.create_table(
        'scheduleexecution',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('schedule_id', sa.Integer(), sa.ForeignKey('schedule.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('trigger', sa.String(), nullable=False, server_default='scheduler'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('error', sa.String(), nullable=True),
    )
    op.create_index('ix_scheduleexecution_schedule_id', 'scheduleexecution', ['schedule_id'])
    op.create_index('ix_scheduleexecution_status', 'scheduleexecution', ['status'])
    op.create_index('ix_scheduleexecution_started_at', 'scheduleexecution', ['started_at'])


def downgrade() -> None:
    op.drop_index('ix_scheduleexecution_started_at', table_name='scheduleexecution')
    op.drop_index('ix_scheduleexecution_status', table_name='scheduleexecution')
    op.drop_index('ix_scheduleexecution_schedule_id', table_name='scheduleexecution')
    op.drop_table('scheduleexecution')
    op.drop_index('ix_schedule_reactor_id', table_name='schedule')
    op.drop_index('ix_schedule_next_run_at', table_name='schedule')
    op.drop_index('ix_schedule_target_type', table_name='schedule')
    op.drop_index('ix_schedule_schedule_type', table_name='schedule')
    op.drop_index('ix_schedule_is_enabled', table_name='schedule')
    op.drop_table('schedule')
