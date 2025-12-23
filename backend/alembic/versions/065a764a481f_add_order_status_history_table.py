"""add_order_status_history_table

Revision ID: 065a764a481f
Revises: b11d15f043a1
Create Date: 2025-12-22 01:58:44.133995

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "065a764a481f"
down_revision: Union[str, Sequence[str], None] = "b11d15f043a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create order_status_history table."""
    op.create_table(
        "order_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("orders.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column(
            "transitioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create index for efficient querying by order_id
    op.create_index(
        "ix_order_status_history_order_id",
        "order_status_history",
        ["order_id"],
    )


def downgrade() -> None:
    """Drop order_status_history table."""
    op.drop_index("ix_order_status_history_order_id", table_name="order_status_history")
    op.drop_table("order_status_history")
