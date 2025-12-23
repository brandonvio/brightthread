"""seed_order_status_history

Revision ID: c2a8b9f1e3d5
Revises: 065a764a481f
Create Date: 2025-12-22 02:30:00.000000

"""

import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
from sqlalchemy import DateTime, String, column, table
from sqlalchemy.dialects.postgresql import UUID

# Add scripts to path for seed data import
scripts_path = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

from seed_data import get_order_status_history

# revision identifiers, used by Alembic.
revision: str = "c2a8b9f1e3d5"
down_revision: Union[str, Sequence[str], None] = "065a764a481f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


order_status_history_table = table(
    "order_status_history",
    column("id", UUID),
    column("order_id", UUID),
    column("status", String),
    column("transitioned_at", DateTime),
)


def upgrade() -> None:
    """Seed order status history data."""
    op.bulk_insert(order_status_history_table, get_order_status_history())


def downgrade() -> None:
    """Remove seeded order status history data."""
    op.execute("DELETE FROM order_status_history")
