"""empty message

Revision ID: 0fb7a4d63b54
Revises: 5305d59d0470, cc41387a2816
Create Date: 2025-06-18 09:53:03.481522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fb7a4d63b54'
down_revision: Union[str, None] = ('5305d59d0470', 'cc41387a2816')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
