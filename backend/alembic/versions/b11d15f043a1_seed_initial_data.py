"""seed_initial_data

Revision ID: b11d15f043a1
Revises: 1a57152a2fa3
Create Date: 2025-12-21 20:20:06.573414

"""

import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    table,
    column,
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
    get_orders,
    get_products,
    get_shipping_addresses,
    get_sizes,
    get_suppliers,
    get_users,
)

# revision identifiers, used by Alembic.
revision: str = "b11d15f043a1"
down_revision: Union[str, Sequence[str], None] = "1a57152a2fa3"
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


def upgrade() -> None:
    """Seed initial data into all tables."""
    # Insert in dependency order
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


def downgrade() -> None:
    """Remove all seeded data."""
    # Delete in reverse dependency order
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
