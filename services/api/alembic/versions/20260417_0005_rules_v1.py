"""add rules and rule executions for automation v1

Revision ID: 20260417_0005
Revises: 20260417_0004
Create Date: 2026-04-17 22:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260417_0005'
down_revision: Union[str, None] = '20260417_0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('trigger_type', sa.String(), nullable=False),
        sa.Column('condition_type', sa.String(), nullable=False),
        sa.Column('condition_config', sa.JSON(), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('action_config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_evaluated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rule') as batch_op:
        batch_op.create_index('ix_rule_is_enabled', ['is_enabled'], unique=False)
        batch_op.create_index('ix_rule_trigger_type', ['trigger_type'], unique=False)
        batch_op.create_index('ix_rule_action_type', ['action_type'], unique=False)
        batch_op.create_index('ix_rule_updated_at', ['updated_at'], unique=False)

    op.create_table(
        'ruleexecution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('dry_run', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('evaluation_summary', sa.JSON(), nullable=False),
        sa.Column('action_result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('ruleexecution') as batch_op:
        batch_op.create_index('ix_ruleexecution_rule_id', ['rule_id'], unique=False)
        batch_op.create_index('ix_ruleexecution_status', ['status'], unique=False)
        batch_op.create_index('ix_ruleexecution_created_at', ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('ruleexecution') as batch_op:
        batch_op.drop_index('ix_ruleexecution_created_at')
        batch_op.drop_index('ix_ruleexecution_status')
        batch_op.drop_index('ix_ruleexecution_rule_id')
    op.drop_table('ruleexecution')

    with op.batch_alter_table('rule') as batch_op:
        batch_op.drop_index('ix_rule_updated_at')
        batch_op.drop_index('ix_rule_action_type')
        batch_op.drop_index('ix_rule_trigger_type')
        batch_op.drop_index('ix_rule_is_enabled')
    op.drop_table('rule')
