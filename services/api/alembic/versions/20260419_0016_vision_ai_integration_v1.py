"""vision ai integration v1

Revision ID: 20260419_0016
Revises: 20260419_0015
Create Date: 2026-04-19 14:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0016'
down_revision: str | None = '20260419_0015'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'visionanalysis',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('photo_id', sa.Integer(), sa.ForeignKey('photo.id'), nullable=False),
        sa.Column('reactor_id', sa.Integer(), sa.ForeignKey('reactor.id'), nullable=True),
        sa.Column('analysis_type', sa.String(), nullable=False, server_default='basic'),
        sa.Column('status', sa.String(), nullable=False, server_default='ok'),
        sa.Column('result', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.create_index('ix_visionanalysis_photo_id', 'visionanalysis', ['photo_id'])
    op.create_index('ix_visionanalysis_reactor_id', 'visionanalysis', ['reactor_id'])
    op.create_index('ix_visionanalysis_analysis_type', 'visionanalysis', ['analysis_type'])
    op.create_index('ix_visionanalysis_status', 'visionanalysis', ['status'])
    op.create_index('ix_visionanalysis_created_at', 'visionanalysis', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_visionanalysis_created_at', table_name='visionanalysis')
    op.drop_index('ix_visionanalysis_status', table_name='visionanalysis')
    op.drop_index('ix_visionanalysis_analysis_type', table_name='visionanalysis')
    op.drop_index('ix_visionanalysis_reactor_id', table_name='visionanalysis')
    op.drop_index('ix_visionanalysis_photo_id', table_name='visionanalysis')
    op.drop_table('visionanalysis')
