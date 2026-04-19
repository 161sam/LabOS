"""command ack retry v1

Revision ID: 20260419_0014
Revises: 20260419_0013
Create Date: 2026-04-19 12:00:00.000000
"""

from collections.abc import Sequence
import uuid

from alembic import op
import sqlalchemy as sa


revision: str = '20260419_0014'
down_revision: str | None = '20260419_0013'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('reactorcommand', sa.Column('command_uid', sa.String(), nullable=True))
    op.add_column('reactorcommand', sa.Column('published_at', sa.DateTime(), nullable=True))
    op.add_column('reactorcommand', sa.Column('acknowledged_at', sa.DateTime(), nullable=True))
    op.add_column('reactorcommand', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('reactorcommand', sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('reactorcommand', sa.Column('last_error', sa.String(), nullable=True))
    op.add_column('reactorcommand', sa.Column('timeout_at', sa.DateTime(), nullable=True))
    op.add_column('reactorcommand', sa.Column('ack_payload', sa.JSON(), nullable=True))
    op.add_column(
        'reactorcommand',
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )

    connection = op.get_bind()
    existing = connection.execute(sa.text('SELECT id FROM reactorcommand WHERE command_uid IS NULL')).fetchall()
    for row in existing:
        connection.execute(
            sa.text('UPDATE reactorcommand SET command_uid = :uid WHERE id = :id'),
            {'uid': uuid.uuid4().hex, 'id': row[0]},
        )

    with op.batch_alter_table('reactorcommand') as batch_op:
        batch_op.alter_column('command_uid', nullable=False)

    op.create_index('ix_reactorcommand_command_uid', 'reactorcommand', ['command_uid'], unique=True)
    op.create_index('ix_reactorcommand_timeout_at', 'reactorcommand', ['timeout_at'])


def downgrade() -> None:
    op.drop_index('ix_reactorcommand_timeout_at', table_name='reactorcommand')
    op.drop_index('ix_reactorcommand_command_uid', table_name='reactorcommand')
    op.drop_column('reactorcommand', 'updated_at')
    op.drop_column('reactorcommand', 'ack_payload')
    op.drop_column('reactorcommand', 'timeout_at')
    op.drop_column('reactorcommand', 'last_error')
    op.drop_column('reactorcommand', 'max_retries')
    op.drop_column('reactorcommand', 'retry_count')
    op.drop_column('reactorcommand', 'acknowledged_at')
    op.drop_column('reactorcommand', 'published_at')
    op.drop_column('reactorcommand', 'command_uid')
