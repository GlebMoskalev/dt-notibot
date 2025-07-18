"""add notificated_events table

Revision ID: 65c2e5a8b444
Revises: 00f084a4654c
Create Date: 2025-05-25 22:44:09.377893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65c2e5a8b444'
down_revision: Union[str, None] = '00f084a4654c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notificated_events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notificated_events')
    # ### end Alembic commands ###
