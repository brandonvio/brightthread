"""reseed_expanded_orders_data

Revision ID: 946a2a66620e
Revises: e4744c7d9a76
Create Date: 2025-12-22 15:54:42.947424

This migration:
1. Ensures order_status_history table exists (creates if missing)
2. Deletes ALL data from all tables
3. Reseeds everything with fresh data including expanded orders for john.smith
"""

import sys
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    column,
    table,
)
from sqlalchemy.dialects.postgresql import UUID

# Add scripts to path for seed data import
scripts_path = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

from seed_data import (
    get_artworks,
    get_colors,
    get_companies,
    get_inventory,
    get_order_line_items,
    get_order_status_history,
    get_orders,
    get_products,
    get_shipping_addresses,
    get_sizes,
    get_suppliers,
    get_users,
)

# revision identifiers, used by Alembic.
revision: str = "946a2a66620e"
down_revision: Union[str, Sequence[str], None] = "e4744c7d9a76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Table definitions for bulk_insert
companies_table = table(
    "companies",
    column("id", UUID),
    column("name", String),
    column("created_at", DateTime),
)

suppliers_table = table(
    "suppliers",
    column("id", UUID),
    column("name", String),
    column("contact_email", String),
    column("phone", String),
    column("address", Text),
    column("created_at", DateTime),
)

products_table = table(
    "products",
    column("id", UUID),
    column("supplier_id", UUID),
    column("sku", String),
    column("name", String),
    column("description", Text),
    column("base_price", Numeric),
    column("created_at", DateTime),
)

colors_table = table(
    "colors",
    column("id", UUID),
    column("name", String),
    column("hex_code", String),
)

sizes_table = table(
    "sizes",
    column("id", UUID),
    column("name", String),
    column("code", String),
    column("sort_order", Integer),
)

inventory_table = table(
    "inventory",
    column("id", UUID),
    column("product_id", UUID),
    column("color_id", UUID),
    column("size_id", UUID),
    column("available_qty", Integer),
    column("reserved_qty", Integer),
    column("updated_at", DateTime),
)

users_table = table(
    "users",
    column("id", UUID),
    column("company_id", UUID),
    column("email", String),
    column("password_hash", String),
    column("created_at", DateTime),
)

artworks_table = table(
    "artworks",
    column("id", UUID),
    column("uploaded_by_user_id", UUID),
    column("name", String),
    column("file_url", String),
    column("file_type", String),
    column("width_px", Integer),
    column("height_px", Integer),
    column("is_active", Boolean),
    column("created_at", DateTime),
)

shipping_addresses_table = table(
    "shipping_addresses",
    column("id", UUID),
    column("created_by_user_id", UUID),
    column("label", String),
    column("street_address", Text),
    column("city", String),
    column("state", String),
    column("postal_code", String),
    column("country", String),
    column("is_default", Boolean),
    column("created_at", DateTime),
)

orders_table = table(
    "orders",
    column("id", UUID),
    column("user_id", UUID),
    column("shipping_address_id", UUID),
    column("artwork_id", UUID),
    column("status", String),
    column("delivery_date", Date),
    column("total_amount", Numeric),
    column("created_at", DateTime),
    column("updated_at", DateTime),
)

order_line_items_table = table(
    "order_line_items",
    column("id", UUID),
    column("order_id", UUID),
    column("inventory_id", UUID),
    column("quantity", Integer),
    column("unit_price", Numeric),
)

order_status_history_table = table(
    "order_status_history",
    column("id", UUID),
    column("order_id", UUID),
    column("status", String),
    column("transitioned_at", DateTime),
)


def _table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :name)"
        ),
        {"name": table_name},
    )
    return result.scalar()


def upgrade() -> None:
    """Delete all data and reseed everything fresh."""
    # Ensure order_status_history table exists
    if not _table_exists("order_status_history"):
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
        op.create_index(
            "ix_order_status_history_order_id",
            "order_status_history",
            ["order_id"],
        )

    # Delete ALL data in reverse dependency order
    op.execute("DELETE FROM order_status_history")
    op.execute("DELETE FROM order_line_items")
    op.execute("DELETE FROM orders")
    op.execute("DELETE FROM shipping_addresses")
    op.execute("DELETE FROM artworks")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM inventory")
    op.execute("DELETE FROM sizes")
    op.execute("DELETE FROM colors")
    op.execute("DELETE FROM products")
    op.execute("DELETE FROM suppliers")
    op.execute("DELETE FROM companies")

    # Insert fresh data in dependency order
    op.bulk_insert(companies_table, get_companies())
    op.bulk_insert(suppliers_table, get_suppliers())
    op.bulk_insert(products_table, get_products())
    op.bulk_insert(colors_table, get_colors())
    op.bulk_insert(sizes_table, get_sizes())
    op.bulk_insert(inventory_table, get_inventory())
    op.bulk_insert(users_table, get_users())
    op.bulk_insert(artworks_table, get_artworks())
    op.bulk_insert(shipping_addresses_table, get_shipping_addresses())
    op.bulk_insert(orders_table, get_orders())
    op.bulk_insert(order_line_items_table, get_order_line_items())
    op.bulk_insert(order_status_history_table, get_order_status_history())


def downgrade() -> None:
    """Remove all seeded data."""
    op.execute("DELETE FROM order_status_history")
    op.execute("DELETE FROM order_line_items")
    op.execute("DELETE FROM orders")
    op.execute("DELETE FROM shipping_addresses")
    op.execute("DELETE FROM artworks")
    op.execute("DELETE FROM users")
    op.execute("DELETE FROM inventory")
    op.execute("DELETE FROM sizes")
    op.execute("DELETE FROM colors")
    op.execute("DELETE FROM products")
    op.execute("DELETE FROM suppliers")
    op.execute("DELETE FROM companies")
