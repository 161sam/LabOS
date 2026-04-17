"""extend task and alert schema for operations v1

Revision ID: 20260417_0003
Revises: 20260417_0002
Create Date: 2026-04-17 16:05:00
"""

from datetime import datetime, time, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260417_0003'
down_revision: Union[str, None] = '20260417_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    task_table = sa.table(
        'task',
        sa.column('id', sa.Integer()),
        sa.column('status', sa.String()),
        sa.column('due_date', sa.Date()),
        sa.column('priority', sa.String()),
        sa.column('due_at', sa.DateTime()),
        sa.column('completed_at', sa.DateTime()),
    )
    alert_table = sa.table(
        'alert',
        sa.column('id', sa.Integer()),
        sa.column('level', sa.String()),
        sa.column('message', sa.String()),
        sa.column('status', sa.String()),
        sa.column('title', sa.String()),
        sa.column('severity', sa.String()),
        sa.column('source_type', sa.String()),
    )

    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(), nullable=False, server_default='normal'))
        batch_op.add_column(sa.Column('due_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('charge_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('reactor_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.add_column(sa.Column('completed_at', sa.DateTime(), nullable=True))

    bind = op.get_bind()
    task_rows = bind.execute(sa.select(task_table.c.id, task_table.c.due_date, task_table.c.status)).fetchall()
    for row in task_rows:
        due_at = datetime.combine(row.due_date, time.min) if row.due_date is not None else None
        completed_at = datetime.now(timezone.utc).replace(tzinfo=None) if row.status == 'done' else None
        bind.execute(
            task_table.update()
            .where(task_table.c.id == row.id)
            .values(due_at=due_at, priority='normal', completed_at=completed_at)
        )

    with op.batch_alter_table('task') as batch_op:
        batch_op.create_index('ix_task_status', ['status'], unique=False)
        batch_op.create_index('ix_task_priority', ['priority'], unique=False)
        batch_op.create_index('ix_task_due_at', ['due_at'], unique=False)
        batch_op.create_index('ix_task_charge_id', ['charge_id'], unique=False)
        batch_op.create_index('ix_task_reactor_id', ['reactor_id'], unique=False)
        batch_op.drop_column('due_date')

    with op.batch_alter_table('alert') as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('severity', sa.String(), nullable=False, server_default='info'))
        batch_op.add_column(sa.Column('source_type', sa.String(), nullable=False, server_default='system'))
        batch_op.add_column(sa.Column('source_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('acknowledged_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('resolved_at', sa.DateTime(), nullable=True))

    alert_rows = bind.execute(
        sa.select(alert_table.c.id, alert_table.c.level, alert_table.c.message, alert_table.c.status)
    ).fetchall()
    for row in alert_rows:
        bind.execute(
            alert_table.update()
            .where(alert_table.c.id == row.id)
            .values(
                title=(row.message or 'Legacy Alert')[:160],
                severity=row.level or 'info',
                source_type='system',
            )
        )

    with op.batch_alter_table('alert') as batch_op:
        batch_op.alter_column('title', existing_type=sa.String(), nullable=False)
        batch_op.create_index('ix_alert_severity', ['severity'], unique=False)
        batch_op.create_index('ix_alert_status', ['status'], unique=False)
        batch_op.create_index('ix_alert_source_type', ['source_type'], unique=False)
        batch_op.create_index('ix_alert_created_at', ['created_at'], unique=False)
        batch_op.drop_column('level')


def downgrade() -> None:
    with op.batch_alter_table('alert') as batch_op:
        batch_op.add_column(sa.Column('level', sa.String(), nullable=False, server_default='info'))

    bind = op.get_bind()
    alert_table = sa.table(
        'alert',
        sa.column('id', sa.Integer()),
        sa.column('severity', sa.String()),
    )
    alert_rows = bind.execute(sa.select(alert_table.c.id, alert_table.c.severity)).fetchall()
    for row in alert_rows:
        bind.execute(
            alert_table.update().where(alert_table.c.id == row.id).values(level=row.severity or 'info')
        )

    with op.batch_alter_table('alert') as batch_op:
        batch_op.drop_index('ix_alert_created_at')
        batch_op.drop_index('ix_alert_source_type')
        batch_op.drop_index('ix_alert_status')
        batch_op.drop_index('ix_alert_severity')
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('acknowledged_at')
        batch_op.drop_column('source_id')
        batch_op.drop_column('source_type')
        batch_op.drop_column('severity')
        batch_op.drop_column('title')
        batch_op.alter_column('level', server_default=None)

    with op.batch_alter_table('task') as batch_op:
        batch_op.add_column(sa.Column('due_date', sa.Date(), nullable=True))

    task_table = sa.table(
        'task',
        sa.column('id', sa.Integer()),
        sa.column('due_at', sa.DateTime()),
        sa.column('due_date', sa.Date()),
    )
    task_rows = bind.execute(sa.select(task_table.c.id, task_table.c.due_at)).fetchall()
    for row in task_rows:
        bind.execute(
            task_table.update()
            .where(task_table.c.id == row.id)
            .values(due_date=row.due_at.date() if row.due_at is not None else None)
        )

    with op.batch_alter_table('task') as batch_op:
        batch_op.drop_index('ix_task_reactor_id')
        batch_op.drop_index('ix_task_charge_id')
        batch_op.drop_index('ix_task_due_at')
        batch_op.drop_index('ix_task_priority')
        batch_op.drop_index('ix_task_status')
        batch_op.drop_column('completed_at')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('reactor_id')
        batch_op.drop_column('charge_id')
        batch_op.drop_column('due_at')
        batch_op.drop_column('priority')
        batch_op.drop_column('description')
