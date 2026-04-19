"""sensor vision fusion / reactor health v1

Revision ID: 20260419_0017
Revises: 20260419_0016
Create Date: 2026-04-19 16:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0017'
down_revision: str | None = '20260419_0016'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'reactorhealthassessment',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reactor_id', sa.Integer(), sa.ForeignKey('reactor.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='unknown'),
        sa.Column('summary', sa.String(), nullable=False, server_default=''),
        sa.Column('signals', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('source_telemetry_at', sa.DateTime(), nullable=True),
        sa.Column('source_vision_analysis_id', sa.Integer(), sa.ForeignKey('visionanalysis.id'), nullable=True),
        sa.Column('source_incident_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('assessed_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_reactorhealthassessment_reactor_id', 'reactorhealthassessment', ['reactor_id'])
    op.create_index('ix_reactorhealthassessment_status', 'reactorhealthassessment', ['status'])
    op.create_index('ix_reactorhealthassessment_assessed_at', 'reactorhealthassessment', ['assessed_at'])
    op.create_index('ix_reactorhealthassessment_created_at', 'reactorhealthassessment', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_reactorhealthassessment_created_at', table_name='reactorhealthassessment')
    op.drop_index('ix_reactorhealthassessment_assessed_at', table_name='reactorhealthassessment')
    op.drop_index('ix_reactorhealthassessment_status', table_name='reactorhealthassessment')
    op.drop_index('ix_reactorhealthassessment_reactor_id', table_name='reactorhealthassessment')
    op.drop_table('reactorhealthassessment')
