"""fix_user_password_hashes

Revision ID: 600e40846231
Revises: c2a8b9f1e3d5
Create Date: 2025-12-22 02:23:03.050658

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "600e40846231"
down_revision: Union[str, Sequence[str], None] = "b11d15f043a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Valid bcrypt hash for "password123"
VALID_PASSWORD_HASH = "$2b$12$47HDOC4jq3EOSYXNPjJes.IcgQ4MKTez0ik2n/f8cNm55spFsjPm6"

# Old placeholder hash that doesn't work
OLD_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.J5z5Y5z5Y5z5Y5"


def upgrade() -> None:
    """Update all user password hashes to valid bcrypt hash for 'password123'."""
    op.execute(f"UPDATE users SET password_hash = '{VALID_PASSWORD_HASH}'")


def downgrade() -> None:
    """Revert to old placeholder hash."""
    op.execute(f"UPDATE users SET password_hash = '{OLD_PASSWORD_HASH}'")
