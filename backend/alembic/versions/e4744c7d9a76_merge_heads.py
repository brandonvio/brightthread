"""merge_heads

Revision ID: e4744c7d9a76
Revises: 600e40846231, c2a8b9f1e3d5
Create Date: 2025-12-22 15:54:33.065822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4744c7d9a76'
down_revision: Union[str, Sequence[str], None] = ('600e40846231', 'c2a8b9f1e3d5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
