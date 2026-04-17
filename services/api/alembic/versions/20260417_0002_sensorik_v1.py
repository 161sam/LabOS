"""extend sensor schema for sensorik v1

Revision ID: 20260417_0002
Revises: 20260417_0001
Create Date: 2026-04-17 15:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260417_0002'
down_revision: Union[str, None] = '20260417_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('sensor') as batch_op:
        batch_op.add_column(sa.Column('location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
            )
        )
        batch_op.add_column(
            sa.Column(
                'updated_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP'),
            )
        )
        batch_op.create_index('ix_sensor_name', ['name'], unique=False)
        batch_op.create_index('ix_sensor_status', ['status'], unique=False)
        batch_op.create_index('ix_sensor_sensor_type', ['sensor_type'], unique=False)
        batch_op.create_index('ix_sensor_reactor_id', ['reactor_id'], unique=False)

    with op.batch_alter_table('sensorvalue') as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(), nullable=True))
        batch_op.create_index('ix_sensorvalue_sensor_id', ['sensor_id'], unique=False)
        batch_op.create_index('ix_sensorvalue_recorded_at', ['recorded_at'], unique=False)
        batch_op.create_index('ix_sensorvalue_sensor_id_recorded_at', ['sensor_id', 'recorded_at'], unique=False)

    op.execute("UPDATE sensor SET status = 'active' WHERE status = 'connected'")


def downgrade() -> None:
    with op.batch_alter_table('sensorvalue') as batch_op:
        batch_op.drop_index('ix_sensorvalue_sensor_id_recorded_at')
        batch_op.drop_index('ix_sensorvalue_recorded_at')
        batch_op.drop_index('ix_sensorvalue_sensor_id')
        batch_op.drop_column('source')

    with op.batch_alter_table('sensor') as batch_op:
        batch_op.drop_index('ix_sensor_reactor_id')
        batch_op.drop_index('ix_sensor_sensor_type')
        batch_op.drop_index('ix_sensor_status')
        batch_op.drop_index('ix_sensor_name')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('notes')
        batch_op.drop_column('location')

    op.execute("UPDATE sensor SET status = 'connected' WHERE status = 'active'")
