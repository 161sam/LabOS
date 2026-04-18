"""add reactorops digital twin v1

Revision ID: 20260418_0010
Revises: 20260418_0009
Create Date: 2026-04-18 17:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260418_0010'
down_revision: Union[str, None] = '20260418_0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reactortwin',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('culture_type', sa.String(), nullable=True),
        sa.Column('strain', sa.String(), nullable=True),
        sa.Column('medium_recipe', sa.String(), nullable=True),
        sa.Column('inoculated_at', sa.DateTime(), nullable=True),
        sa.Column('current_phase', sa.String(), nullable=False, server_default='growth'),
        sa.Column('target_ph_min', sa.Float(), nullable=True),
        sa.Column('target_ph_max', sa.Float(), nullable=True),
        sa.Column('target_temp_min', sa.Float(), nullable=True),
        sa.Column('target_temp_max', sa.Float(), nullable=True),
        sa.Column('target_light_min', sa.Float(), nullable=True),
        sa.Column('target_light_max', sa.Float(), nullable=True),
        sa.Column('target_flow_min', sa.Float(), nullable=True),
        sa.Column('target_flow_max', sa.Float(), nullable=True),
        sa.Column('expected_harvest_window_start', sa.DateTime(), nullable=True),
        sa.Column('expected_harvest_window_end', sa.DateTime(), nullable=True),
        sa.Column('contamination_state', sa.String(), nullable=True),
        sa.Column('technical_state', sa.String(), nullable=False, server_default='nominal'),
        sa.Column('biological_state', sa.String(), nullable=False, server_default='unknown'),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reactor_id', name='uq_reactortwin_reactor_id'),
    )
    with op.batch_alter_table('reactortwin') as batch_op:
        batch_op.create_index('ix_reactortwin_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_reactortwin_current_phase', ['current_phase'], unique=False)
        batch_op.create_index('ix_reactortwin_technical_state', ['technical_state'], unique=False)
        batch_op.create_index('ix_reactortwin_biological_state', ['biological_state'], unique=False)
        batch_op.create_index('ix_reactortwin_contamination_state', ['contamination_state'], unique=False)
        batch_op.create_index(
            'ix_reactortwin_expected_harvest_window_start',
            ['expected_harvest_window_start'],
            unique=False,
        )

    op.create_table(
        'reactorevent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reactor_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('phase_snapshot', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['useraccount.id']),
        sa.ForeignKeyConstraint(['reactor_id'], ['reactor.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('reactorevent') as batch_op:
        batch_op.create_index('ix_reactorevent_reactor_id', ['reactor_id'], unique=False)
        batch_op.create_index('ix_reactorevent_created_by_user_id', ['created_by_user_id'], unique=False)
        batch_op.create_index(
            'ix_reactorevent_reactor_id_created_at',
            ['reactor_id', 'created_at'],
            unique=False,
        )
        batch_op.create_index('ix_reactorevent_event_type', ['event_type'], unique=False)
        batch_op.create_index('ix_reactorevent_severity', ['severity'], unique=False)
        batch_op.create_index('ix_reactorevent_phase_snapshot', ['phase_snapshot'], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO reactortwin (
                reactor_id,
                current_phase,
                technical_state,
                biological_state,
                created_at,
                updated_at
            )
            SELECT
                reactor.id,
                'growth',
                'nominal',
                'unknown',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            FROM reactor
            """
        )
    )


def downgrade() -> None:
    with op.batch_alter_table('reactorevent') as batch_op:
        batch_op.drop_index('ix_reactorevent_phase_snapshot')
        batch_op.drop_index('ix_reactorevent_severity')
        batch_op.drop_index('ix_reactorevent_event_type')
        batch_op.drop_index('ix_reactorevent_reactor_id_created_at')
        batch_op.drop_index('ix_reactorevent_created_by_user_id')
        batch_op.drop_index('ix_reactorevent_reactor_id')

    op.drop_table('reactorevent')

    with op.batch_alter_table('reactortwin') as batch_op:
        batch_op.drop_index('ix_reactortwin_expected_harvest_window_start')
        batch_op.drop_index('ix_reactortwin_contamination_state')
        batch_op.drop_index('ix_reactortwin_biological_state')
        batch_op.drop_index('ix_reactortwin_technical_state')
        batch_op.drop_index('ix_reactortwin_current_phase')
        batch_op.drop_index('ix_reactortwin_reactor_id')

    op.drop_table('reactortwin')
