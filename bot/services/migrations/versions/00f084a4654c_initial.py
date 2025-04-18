"""initial

Revision ID: 00f084a4654c
Revises: 
Create Date: 2025-04-12 16:15:10.880074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00f084a4654c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('start_time', sa.TIMESTAMP(), nullable=False),
    sa.Column('end_time', sa.TIMESTAMP(), nullable=False),
    sa.Column('section', sa.Enum('Lecture', 'Break', name='sectionenum'), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('organizers', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invites',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('secret_code', sa.String(length=20), nullable=False),
    sa.Column('role', sa.Enum('User', 'Admin', 'SuperAdmin', name='roleenum'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('role', sa.Enum('User', 'Admin', 'SuperAdmin', name='roleenum'), nullable=False),
    sa.Column('telegram_name', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('favourite_events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.chat_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friends',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('first_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('second_chat_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['first_chat_id'], ['users.chat_id'], ),
    sa.ForeignKeyConstraint(['second_chat_id'], ['users.chat_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('friendship_invites',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sender_id', sa.BigInteger(), nullable=False),
    sa.Column('receiver_id', sa.BigInteger(), nullable=False),
    sa.Column('invite_status', sa.Enum('Pending', 'Approved', 'Rejected', name='invitestatusenum'), nullable=False),
    sa.ForeignKeyConstraint(['receiver_id'], ['users.chat_id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.chat_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP TYPE IF EXISTS invitestatusenum CASCADE;")
    op.execute("DROP TYPE IF EXISTS roleenum CASCADE;")
    op.execute("DROP TYPE IF EXISTS sectionenum CASCADE;")
    op.drop_table('friendship_invites')
    op.drop_table('friends')
    op.drop_table('favourite_events')
    op.drop_table('users')
    op.drop_table('invites')
    op.drop_table('events')
    # ### end Alembic commands ###
