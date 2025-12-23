"""Seed data for BrightThread database.

This module provides seed data for development and testing purposes.
Data includes realistic B2B apparel company data following the data model.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from uuid6 import uuid7

# Generate UUIDs using uuid7 for time-ordered IDs
SUPPLIER_IDS = [uuid7() for _ in range(3)]
PRODUCT_IDS = [uuid7() for _ in range(10)]
COLOR_IDS = [uuid7() for _ in range(10)]
SIZE_IDS = [uuid7() for _ in range(7)]
COMPANY_IDS = [uuid7() for _ in range(3)]
USER_IDS = [uuid7() for _ in range(6)]
ARTWORK_IDS = [uuid7() for _ in range(6)]
SHIPPING_ADDRESS_IDS = [uuid7() for _ in range(6)]
ORDER_IDS = [
    uuid7() for _ in range(15)
]  # 8 original + 7 new (one per state for john.smith)
INVENTORY_IDS = [uuid7() for _ in range(90)]  # 6 products × 3 colors × 5 sizes
ORDER_LINE_ITEM_IDS = [
    uuid7() for _ in range(36)
]  # 22 original + 14 new (2 per new order)
ORDER_STATUS_HISTORY_IDS = [
    uuid7() for _ in range(54)
]  # 26 original + 28 new (1+2+3+4+5+6+7)

# Cached inventory data (populated on first call)
_inventory_cache: list[dict] | None = None

# Base timestamp for consistent data
BASE_TIME = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)


def get_suppliers() -> list[dict]:
    """Return seed data for suppliers table."""
    return [
        {
            "id": SUPPLIER_IDS[0],
            "name": "Gildan Brands",
            "contact_email": "orders@gildan.com",
            "phone": "+1-800-555-0101",
            "address": "600 Red Banks Rd\nGreenville, SC 29607",
            "created_at": BASE_TIME,
        },
        {
            "id": SUPPLIER_IDS[1],
            "name": "Bella+Canvas",
            "contact_email": "wholesale@bellacanvas.com",
            "phone": "+1-800-555-0102",
            "address": "1385 S Claudina St\nAnaheim, CA 92805",
            "created_at": BASE_TIME,
        },
        {
            "id": SUPPLIER_IDS[2],
            "name": "Next Level Apparel",
            "contact_email": "sales@nextlevelapparel.com",
            "phone": "+1-800-555-0103",
            "address": "17801 Cartwright Rd\nIrvine, CA 92614",
            "created_at": BASE_TIME,
        },
    ]


def get_products() -> list[dict]:
    """Return seed data for products table."""
    return [
        {
            "id": PRODUCT_IDS[0],
            "supplier_id": SUPPLIER_IDS[0],
            "sku": "GLD-5000-TEE",
            "name": "Gildan Heavy Cotton T-Shirt",
            "description": "Classic fit, 100% cotton t-shirt. 5.3 oz weight.",
            "base_price": Decimal("4.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[1],
            "supplier_id": SUPPLIER_IDS[0],
            "sku": "GLD-18500-HOOD",
            "name": "Gildan Heavy Blend Hoodie",
            "description": "50% cotton, 50% polyester blend hoodie. 8 oz weight.",
            "base_price": Decimal("18.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[2],
            "supplier_id": SUPPLIER_IDS[1],
            "sku": "BC-3001-TEE",
            "name": "Bella+Canvas Unisex Jersey Tee",
            "description": "Soft, retail-fit 100% ring-spun cotton. 4.2 oz.",
            "base_price": Decimal("6.49"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[3],
            "supplier_id": SUPPLIER_IDS[1],
            "sku": "BC-3719-HOOD",
            "name": "Bella+Canvas Sponge Fleece Hoodie",
            "description": "Ultra-soft sponge fleece. 52% cotton, 48% polyester.",
            "base_price": Decimal("24.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[4],
            "supplier_id": SUPPLIER_IDS[2],
            "sku": "NL-6210-TEE",
            "name": "Next Level CVC Crew",
            "description": "Premium fitted crew neck. 60% cotton, 40% polyester.",
            "base_price": Decimal("5.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[5],
            "supplier_id": SUPPLIER_IDS[2],
            "sku": "NL-9301-HOOD",
            "name": "Next Level French Terry Hoodie",
            "description": "Lightweight french terry. 60% cotton, 40% polyester.",
            "base_price": Decimal("22.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[6],
            "supplier_id": SUPPLIER_IDS[0],
            "sku": "GLD-8800-POLO",
            "name": "Gildan DryBlend Polo",
            "description": "Professional polo shirt. 50% cotton, 50% polyester.",
            "base_price": Decimal("12.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[7],
            "supplier_id": SUPPLIER_IDS[1],
            "sku": "BC-8860-CAP",
            "name": "Bella+Canvas Trucker Cap",
            "description": "Classic trucker style with mesh back.",
            "base_price": Decimal("8.99"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[8],
            "supplier_id": SUPPLIER_IDS[2],
            "sku": "NL-6440-TANK",
            "name": "Next Level Premium Tank",
            "description": "Lightweight racerback tank. 100% combed cotton.",
            "base_price": Decimal("4.49"),
            "created_at": BASE_TIME,
        },
        {
            "id": PRODUCT_IDS[9],
            "supplier_id": SUPPLIER_IDS[0],
            "sku": "GLD-12000-CREW",
            "name": "Gildan Crewneck Sweatshirt",
            "description": "Classic crewneck. 50% cotton, 50% polyester.",
            "base_price": Decimal("14.99"),
            "created_at": BASE_TIME,
        },
    ]


def get_colors() -> list[dict]:
    """Return seed data for colors table."""
    return [
        {"id": COLOR_IDS[0], "name": "Navy", "hex_code": "#001F3F"},
        {"id": COLOR_IDS[1], "name": "Black", "hex_code": "#000000"},
        {"id": COLOR_IDS[2], "name": "White", "hex_code": "#FFFFFF"},
        {"id": COLOR_IDS[3], "name": "Red", "hex_code": "#DC3545"},
        {"id": COLOR_IDS[4], "name": "Heather Gray", "hex_code": "#808080"},
        {"id": COLOR_IDS[5], "name": "Royal Blue", "hex_code": "#4169E1"},
        {"id": COLOR_IDS[6], "name": "Forest Green", "hex_code": "#228B22"},
        {"id": COLOR_IDS[7], "name": "Maroon", "hex_code": "#800000"},
        {"id": COLOR_IDS[8], "name": "Charcoal", "hex_code": "#36454F"},
        {"id": COLOR_IDS[9], "name": "Light Blue", "hex_code": "#ADD8E6"},
    ]


def get_sizes() -> list[dict]:
    """Return seed data for sizes table."""
    return [
        {"id": SIZE_IDS[0], "name": "Extra Small", "code": "XS", "sort_order": 1},
        {"id": SIZE_IDS[1], "name": "Small", "code": "S", "sort_order": 2},
        {"id": SIZE_IDS[2], "name": "Medium", "code": "M", "sort_order": 3},
        {"id": SIZE_IDS[3], "name": "Large", "code": "L", "sort_order": 4},
        {"id": SIZE_IDS[4], "name": "Extra Large", "code": "XL", "sort_order": 5},
        {"id": SIZE_IDS[5], "name": "2X Large", "code": "XXL", "sort_order": 6},
        {"id": SIZE_IDS[6], "name": "3X Large", "code": "XXXL", "sort_order": 7},
    ]


def get_companies() -> list[dict]:
    """Return seed data for companies table."""
    return [
        {
            "id": COMPANY_IDS[0],
            "name": "TechStart Inc.",
            "created_at": BASE_TIME,
        },
        {
            "id": COMPANY_IDS[1],
            "name": "Acme Corporation",
            "created_at": BASE_TIME,
        },
        {
            "id": COMPANY_IDS[2],
            "name": "Global Solutions LLC",
            "created_at": BASE_TIME,
        },
    ]


def get_users() -> list[dict]:
    """Return seed data for users table."""
    # Bcrypt hash for "password123"
    password_hash = "$2b$12$47HDOC4jq3EOSYXNPjJes.IcgQ4MKTez0ik2n/f8cNm55spFsjPm6"
    return [
        {
            "id": USER_IDS[0],
            "company_id": COMPANY_IDS[0],
            "email": "john.smith@techstart.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
        {
            "id": USER_IDS[1],
            "company_id": COMPANY_IDS[0],
            "email": "sarah.jones@techstart.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
        {
            "id": USER_IDS[2],
            "company_id": COMPANY_IDS[1],
            "email": "mike.wilson@acme.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
        {
            "id": USER_IDS[3],
            "company_id": COMPANY_IDS[1],
            "email": "lisa.brown@acme.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
        {
            "id": USER_IDS[4],
            "company_id": COMPANY_IDS[2],
            "email": "david.lee@globalsolutions.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
        {
            "id": USER_IDS[5],
            "company_id": COMPANY_IDS[2],
            "email": "emma.davis@globalsolutions.com",
            "password_hash": password_hash,
            "created_at": BASE_TIME,
        },
    ]


def get_artworks() -> list[dict]:
    """Return seed data for artworks table."""
    return [
        {
            "id": ARTWORK_IDS[0],
            "uploaded_by_user_id": USER_IDS[0],
            "name": "TechStart Primary Logo",
            "file_url": "s3://brightthread-artworks/techstart/primary-logo.png",
            "file_type": "png",
            "width_px": 1200,
            "height_px": 400,
            "is_active": True,
            "created_at": BASE_TIME,
        },
        {
            "id": ARTWORK_IDS[1],
            "uploaded_by_user_id": USER_IDS[0],
            "name": "TechStart 2025 Event Badge",
            "file_url": "s3://brightthread-artworks/techstart/event-2025.png",
            "file_type": "png",
            "width_px": 800,
            "height_px": 800,
            "is_active": True,
            "created_at": BASE_TIME,
        },
        {
            "id": ARTWORK_IDS[2],
            "uploaded_by_user_id": USER_IDS[2],
            "name": "Acme Corp Logo",
            "file_url": "s3://brightthread-artworks/acme/logo.svg",
            "file_type": "svg",
            "width_px": 1000,
            "height_px": 300,
            "is_active": True,
            "created_at": BASE_TIME,
        },
        {
            "id": ARTWORK_IDS[3],
            "uploaded_by_user_id": USER_IDS[2],
            "name": "Acme Retro Badge",
            "file_url": "s3://brightthread-artworks/acme/retro-badge.png",
            "file_type": "png",
            "width_px": 600,
            "height_px": 600,
            "is_active": True,
            "created_at": BASE_TIME,
        },
        {
            "id": ARTWORK_IDS[4],
            "uploaded_by_user_id": USER_IDS[4],
            "name": "Global Solutions Logo",
            "file_url": "s3://brightthread-artworks/global/logo.png",
            "file_type": "png",
            "width_px": 1500,
            "height_px": 500,
            "is_active": True,
            "created_at": BASE_TIME,
        },
        {
            "id": ARTWORK_IDS[5],
            "uploaded_by_user_id": USER_IDS[4],
            "name": "Global 25th Anniversary",
            "file_url": "s3://brightthread-artworks/global/25th-anniversary.ai",
            "file_type": "ai",
            "width_px": 2000,
            "height_px": 2000,
            "is_active": True,
            "created_at": BASE_TIME,
        },
    ]


def get_shipping_addresses() -> list[dict]:
    """Return seed data for shipping_addresses table."""
    return [
        {
            "id": SHIPPING_ADDRESS_IDS[0],
            "created_by_user_id": USER_IDS[0],
            "label": "TechStart HQ",
            "street_address": "100 Innovation Drive\nSuite 500",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94107",
            "country": "USA",
            "is_default": True,
            "created_at": BASE_TIME,
        },
        {
            "id": SHIPPING_ADDRESS_IDS[1],
            "created_by_user_id": USER_IDS[0],
            "label": "TechStart Warehouse",
            "street_address": "2500 Logistics Blvd",
            "city": "Oakland",
            "state": "CA",
            "postal_code": "94621",
            "country": "USA",
            "is_default": False,
            "created_at": BASE_TIME,
        },
        {
            "id": SHIPPING_ADDRESS_IDS[2],
            "created_by_user_id": USER_IDS[2],
            "label": "Acme HQ",
            "street_address": "1 Acme Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA",
            "is_default": True,
            "created_at": BASE_TIME,
        },
        {
            "id": SHIPPING_ADDRESS_IDS[3],
            "created_by_user_id": USER_IDS[2],
            "label": "Acme Distribution Center",
            "street_address": "8000 Commerce Way",
            "city": "Indianapolis",
            "state": "IN",
            "postal_code": "46241",
            "country": "USA",
            "is_default": False,
            "created_at": BASE_TIME,
        },
        {
            "id": SHIPPING_ADDRESS_IDS[4],
            "created_by_user_id": USER_IDS[4],
            "label": "Global Solutions HQ",
            "street_address": "555 World Trade Center\nFloor 42",
            "city": "New York",
            "state": "NY",
            "postal_code": "10007",
            "country": "USA",
            "is_default": True,
            "created_at": BASE_TIME,
        },
        {
            "id": SHIPPING_ADDRESS_IDS[5],
            "created_by_user_id": USER_IDS[4],
            "label": "Global West Coast Office",
            "street_address": "1200 Pacific Ave",
            "city": "Seattle",
            "state": "WA",
            "postal_code": "98101",
            "country": "USA",
            "is_default": False,
            "created_at": BASE_TIME,
        },
    ]


def get_inventory() -> list[dict]:
    """Return seed data for inventory table.

    Creates inventory for first 6 products with 3 colors and 5 sizes each.
    Uses cached data to ensure consistent IDs across multiple calls.
    """
    global _inventory_cache
    if _inventory_cache is not None:
        return _inventory_cache

    inventory = []
    inv_idx = 0

    # Generate inventory for first 6 products, 3 colors, 5 sizes each (90 items)
    for prod_idx in range(6):
        for color_idx in range(3):
            for size_idx in range(5):
                inventory.append(
                    {
                        "id": INVENTORY_IDS[inv_idx],
                        "product_id": PRODUCT_IDS[prod_idx],
                        "color_id": COLOR_IDS[color_idx],
                        "size_id": SIZE_IDS[size_idx],
                        "available_qty": 100 + ((inv_idx + 1) * 5),
                        "reserved_qty": (inv_idx + 1) % 20,
                        "updated_at": BASE_TIME,
                    }
                )
                inv_idx += 1

    _inventory_cache = inventory
    return inventory


def get_orders() -> list[dict]:
    """Return seed data for orders table."""
    return [
        {
            "id": ORDER_IDS[0],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[0],
            "status": "CREATED",
            "delivery_date": date(2025, 2, 15),
            "total_amount": Decimal("1249.50"),
            "created_at": BASE_TIME,
            "updated_at": BASE_TIME,
        },
        {
            "id": ORDER_IDS[1],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[1],
            "artwork_id": ARTWORK_IDS[1],
            "status": "APPROVED",
            "delivery_date": date(2025, 2, 20),
            "total_amount": Decimal("2875.00"),
            "created_at": BASE_TIME + timedelta(days=1),
            "updated_at": BASE_TIME + timedelta(days=2),
        },
        {
            "id": ORDER_IDS[2],
            "user_id": USER_IDS[2],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[2],
            "artwork_id": ARTWORK_IDS[2],
            "status": "IN_PRODUCTION",
            "delivery_date": date(2025, 2, 10),
            "total_amount": Decimal("4500.00"),
            "created_at": BASE_TIME + timedelta(days=2),
            "updated_at": BASE_TIME + timedelta(days=5),
        },
        {
            "id": ORDER_IDS[3],
            "user_id": USER_IDS[3],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[3],
            "artwork_id": ARTWORK_IDS[3],
            "status": "READY_TO_SHIP",
            "delivery_date": date(2025, 1, 30),
            "total_amount": Decimal("890.25"),
            "created_at": BASE_TIME + timedelta(days=3),
            "updated_at": BASE_TIME + timedelta(days=7),
        },
        {
            "id": ORDER_IDS[4],
            "user_id": USER_IDS[4],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[4],
            "artwork_id": ARTWORK_IDS[4],
            "status": "DELIVERED",
            "delivery_date": date(2025, 1, 25),
            "total_amount": Decimal("3250.75"),
            "created_at": BASE_TIME + timedelta(days=4),
            "updated_at": BASE_TIME + timedelta(days=11),
        },
        {
            "id": ORDER_IDS[5],
            "user_id": USER_IDS[5],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[5],
            "artwork_id": ARTWORK_IDS[5],
            "status": "CREATED",
            "delivery_date": date(2025, 3, 1),
            "total_amount": Decimal("1875.00"),
            "created_at": BASE_TIME + timedelta(days=5),
            "updated_at": BASE_TIME + timedelta(days=5),
        },
        {
            "id": ORDER_IDS[6],
            "user_id": USER_IDS[1],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[0],
            "status": "APPROVED",
            "delivery_date": date(2025, 2, 28),
            "total_amount": Decimal("5430.00"),
            "created_at": BASE_TIME + timedelta(days=6),
            "updated_at": BASE_TIME + timedelta(days=7),
        },
        {
            "id": ORDER_IDS[7],
            "user_id": USER_IDS[2],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[2],
            "artwork_id": None,
            "status": "CREATED",
            "delivery_date": date(2025, 3, 15),
            "total_amount": Decimal("750.00"),
            "created_at": BASE_TIME + timedelta(days=7),
            "updated_at": BASE_TIME + timedelta(days=7),
        },
        # Orders 9-15: john.smith@techstart.com - one order per lifecycle state
        {
            "id": ORDER_IDS[8],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[0],
            "status": "CREATED",
            "delivery_date": date(2025, 3, 20),
            "total_amount": Decimal("599.00"),
            "created_at": BASE_TIME + timedelta(days=10),
            "updated_at": BASE_TIME + timedelta(days=10),
        },
        {
            "id": ORDER_IDS[9],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[0],
            "status": "APPROVED",
            "delivery_date": date(2025, 3, 18),
            "total_amount": Decimal("1198.00"),
            "created_at": BASE_TIME + timedelta(days=8),
            "updated_at": BASE_TIME + timedelta(days=9),
        },
        {
            "id": ORDER_IDS[10],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[1],
            "status": "IN_PRODUCTION",
            "delivery_date": date(2025, 3, 10),
            "total_amount": Decimal("1797.00"),
            "created_at": BASE_TIME + timedelta(days=5),
            "updated_at": BASE_TIME + timedelta(days=8),
        },
        {
            "id": ORDER_IDS[11],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[1],
            "artwork_id": ARTWORK_IDS[0],
            "status": "READY_TO_SHIP",
            "delivery_date": date(2025, 2, 25),
            "total_amount": Decimal("2396.00"),
            "created_at": BASE_TIME + timedelta(days=3),
            "updated_at": BASE_TIME + timedelta(days=10),
        },
        {
            "id": ORDER_IDS[12],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[1],
            "status": "SHIPPED",
            "delivery_date": date(2025, 2, 20),
            "total_amount": Decimal("2995.00"),
            "created_at": BASE_TIME + timedelta(days=1),
            "updated_at": BASE_TIME + timedelta(days=12),
        },
        {
            "id": ORDER_IDS[13],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[0],
            "artwork_id": ARTWORK_IDS[0],
            "status": "DELIVERED",
            "delivery_date": date(2025, 2, 10),
            "total_amount": Decimal("3594.00"),
            "created_at": BASE_TIME - timedelta(days=10),
            "updated_at": BASE_TIME + timedelta(days=5),
        },
        {
            "id": ORDER_IDS[14],
            "user_id": USER_IDS[0],
            "shipping_address_id": SHIPPING_ADDRESS_IDS[1],
            "artwork_id": ARTWORK_IDS[1],
            "status": "RETURNED",
            "delivery_date": date(2025, 1, 20),
            "total_amount": Decimal("4193.00"),
            "created_at": BASE_TIME - timedelta(days=20),
            "updated_at": BASE_TIME + timedelta(days=10),
        },
    ]


def get_order_line_items() -> list[dict]:
    """Return seed data for order_line_items table.

    Uses varied products across orders:
    - Product 0 (Gildan T-Shirt $4.99): indices 0-14
    - Product 1 (Gildan Hoodie $18.99): indices 15-29
    - Product 2 (Bella+Canvas Tee $6.49): indices 30-44
    - Product 3 (Bella+Canvas Hoodie $24.99): indices 45-59
    - Product 4 (Next Level Crew $5.99): indices 60-74
    - Product 5 (Next Level Hoodie $22.99): indices 75-89
    """
    inventory = get_inventory()
    return [
        # Order 1 - Mixed: Gildan T-Shirt + Bella+Canvas Tee + Next Level Crew
        {
            "id": ORDER_LINE_ITEM_IDS[0],
            "order_id": ORDER_IDS[0],
            "inventory_id": inventory[0]["id"],  # Gildan T-Shirt, Navy, XS
            "quantity": 50,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[1],
            "order_id": ORDER_IDS[0],
            "inventory_id": inventory[32]["id"],  # Bella+Canvas Tee, Black, M
            "quantity": 50,
            "unit_price": Decimal("6.49"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[2],
            "order_id": ORDER_IDS[0],
            "inventory_id": inventory[63]["id"],  # Next Level Crew, Black, L
            "quantity": 100,
            "unit_price": Decimal("5.99"),
        },
        # Order 2 - Mixed: Gildan Hoodie + Next Level Hoodie
        {
            "id": ORDER_LINE_ITEM_IDS[3],
            "order_id": ORDER_IDS[1],
            "inventory_id": inventory[17]["id"],  # Gildan Hoodie, Navy, M
            "quantity": 75,
            "unit_price": Decimal("18.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[4],
            "order_id": ORDER_IDS[1],
            "inventory_id": inventory[78]["id"],  # Next Level Hoodie, Navy, L
            "quantity": 75,
            "unit_price": Decimal("22.99"),
        },
        # Order 3 - Mixed: All T-Shirts (Gildan, Bella+Canvas, Next Level)
        {
            "id": ORDER_LINE_ITEM_IDS[5],
            "order_id": ORDER_IDS[2],
            "inventory_id": inventory[2]["id"],  # Gildan T-Shirt, Navy, M
            "quantity": 100,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[6],
            "order_id": ORDER_IDS[2],
            "inventory_id": inventory[33]["id"],  # Bella+Canvas Tee, Black, L
            "quantity": 100,
            "unit_price": Decimal("6.49"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[7],
            "order_id": ORDER_IDS[2],
            "inventory_id": inventory[64]["id"],  # Next Level Crew, Black, XL
            "quantity": 100,
            "unit_price": Decimal("5.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[8],
            "order_id": ORDER_IDS[2],
            "inventory_id": inventory[10]["id"],  # Gildan T-Shirt, White, XS
            "quantity": 100,
            "unit_price": Decimal("4.99"),
        },
        # Order 4 - Mixed: Bella+Canvas Hoodie + Gildan Hoodie
        {
            "id": ORDER_LINE_ITEM_IDS[9],
            "order_id": ORDER_IDS[3],
            "inventory_id": inventory[47]["id"],  # Bella+Canvas Hoodie, Navy, M
            "quantity": 30,
            "unit_price": Decimal("24.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[10],
            "order_id": ORDER_IDS[3],
            "inventory_id": inventory[18]["id"],  # Gildan Hoodie, Navy, L
            "quantity": 30,
            "unit_price": Decimal("18.99"),
        },
        # Order 5 - Premium Hoodies: Bella+Canvas + Next Level
        {
            "id": ORDER_LINE_ITEM_IDS[11],
            "order_id": ORDER_IDS[4],
            "inventory_id": inventory[48]["id"],  # Bella+Canvas Hoodie, Navy, L
            "quantity": 50,
            "unit_price": Decimal("24.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[12],
            "order_id": ORDER_IDS[4],
            "inventory_id": inventory[79]["id"],  # Next Level Hoodie, Navy, XL
            "quantity": 50,
            "unit_price": Decimal("22.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[13],
            "order_id": ORDER_IDS[4],
            "inventory_id": inventory[56]["id"],  # Bella+Canvas Hoodie, Black, S
            "quantity": 30,
            "unit_price": Decimal("24.99"),
        },
        # Order 6 - Budget T-Shirts: Gildan + Next Level
        {
            "id": ORDER_LINE_ITEM_IDS[14],
            "order_id": ORDER_IDS[5],
            "inventory_id": inventory[3]["id"],  # Gildan T-Shirt, Navy, L
            "quantity": 100,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[15],
            "order_id": ORDER_IDS[5],
            "inventory_id": inventory[65]["id"],  # Next Level Crew, White, XS
            "quantity": 75,
            "unit_price": Decimal("5.99"),
        },
        # Order 7 - Large variety order
        {
            "id": ORDER_LINE_ITEM_IDS[16],
            "order_id": ORDER_IDS[6],
            "inventory_id": inventory[5]["id"],  # Gildan T-Shirt, Black, XS
            "quantity": 100,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[17],
            "order_id": ORDER_IDS[6],
            "inventory_id": inventory[20]["id"],  # Gildan Hoodie, Black, XS
            "quantity": 100,
            "unit_price": Decimal("18.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[18],
            "order_id": ORDER_IDS[6],
            "inventory_id": inventory[35]["id"],  # Bella+Canvas Tee, Black, XS
            "quantity": 100,
            "unit_price": Decimal("6.49"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[19],
            "order_id": ORDER_IDS[6],
            "inventory_id": inventory[50]["id"],  # Bella+Canvas Hoodie, Black, XS
            "quantity": 100,
            "unit_price": Decimal("24.99"),
        },
        # Order 8 - Mixed hoodies
        {
            "id": ORDER_LINE_ITEM_IDS[20],
            "order_id": ORDER_IDS[7],
            "inventory_id": inventory[22]["id"],  # Gildan Hoodie, Black, M
            "quantity": 25,
            "unit_price": Decimal("18.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[21],
            "order_id": ORDER_IDS[7],
            "inventory_id": inventory[80]["id"],  # Next Level Hoodie, Black, XS
            "quantity": 25,
            "unit_price": Decimal("22.99"),
        },
        # Order 9 (john.smith CREATED) - T-Shirt + Hoodie combo
        {
            "id": ORDER_LINE_ITEM_IDS[22],
            "order_id": ORDER_IDS[8],
            "inventory_id": inventory[1]["id"],  # Gildan T-Shirt, Navy, S
            "quantity": 50,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[23],
            "order_id": ORDER_IDS[8],
            "inventory_id": inventory[16]["id"],  # Gildan Hoodie, Navy, S
            "quantity": 25,
            "unit_price": Decimal("18.99"),
        },
        # Order 10 (john.smith APPROVED) - Bella+Canvas mix
        {
            "id": ORDER_LINE_ITEM_IDS[24],
            "order_id": ORDER_IDS[9],
            "inventory_id": inventory[31]["id"],  # Bella+Canvas Tee, Black, S
            "quantity": 100,
            "unit_price": Decimal("6.49"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[25],
            "order_id": ORDER_IDS[9],
            "inventory_id": inventory[46]["id"],  # Bella+Canvas Hoodie, Navy, S
            "quantity": 50,
            "unit_price": Decimal("24.99"),
        },
        # Order 11 (john.smith IN_PRODUCTION) - Next Level mix
        {
            "id": ORDER_LINE_ITEM_IDS[26],
            "order_id": ORDER_IDS[10],
            "inventory_id": inventory[62]["id"],  # Next Level Crew, Black, M
            "quantity": 150,
            "unit_price": Decimal("5.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[27],
            "order_id": ORDER_IDS[10],
            "inventory_id": inventory[77]["id"],  # Next Level Hoodie, Navy, M
            "quantity": 75,
            "unit_price": Decimal("22.99"),
        },
        # Order 12 (john.smith READY_TO_SHIP) - Mixed brands T-Shirts
        {
            "id": ORDER_LINE_ITEM_IDS[28],
            "order_id": ORDER_IDS[11],
            "inventory_id": inventory[4]["id"],  # Gildan T-Shirt, Navy, XL
            "quantity": 100,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[29],
            "order_id": ORDER_IDS[11],
            "inventory_id": inventory[34]["id"],  # Bella+Canvas Tee, Black, XL
            "quantity": 100,
            "unit_price": Decimal("6.49"),
        },
        # Order 13 (john.smith SHIPPED) - All hoodies
        {
            "id": ORDER_LINE_ITEM_IDS[30],
            "order_id": ORDER_IDS[12],
            "inventory_id": inventory[19]["id"],  # Gildan Hoodie, Navy, XL
            "quantity": 100,
            "unit_price": Decimal("18.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[31],
            "order_id": ORDER_IDS[12],
            "inventory_id": inventory[49]["id"],  # Bella+Canvas Hoodie, Navy, XL
            "quantity": 50,
            "unit_price": Decimal("24.99"),
        },
        # Order 14 (john.smith DELIVERED) - Large mixed order
        {
            "id": ORDER_LINE_ITEM_IDS[32],
            "order_id": ORDER_IDS[13],
            "inventory_id": inventory[7]["id"],  # Gildan T-Shirt, Black, M
            "quantity": 200,
            "unit_price": Decimal("4.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[33],
            "order_id": ORDER_IDS[13],
            "inventory_id": inventory[82]["id"],  # Next Level Hoodie, Black, M
            "quantity": 100,
            "unit_price": Decimal("22.99"),
        },
        # Order 15 (john.smith RETURNED) - Premium items
        {
            "id": ORDER_LINE_ITEM_IDS[34],
            "order_id": ORDER_IDS[14],
            "inventory_id": inventory[53]["id"],  # Bella+Canvas Hoodie, Navy, L
            "quantity": 150,
            "unit_price": Decimal("24.99"),
        },
        {
            "id": ORDER_LINE_ITEM_IDS[35],
            "order_id": ORDER_IDS[14],
            "inventory_id": inventory[83]["id"],  # Next Level Hoodie, Black, L
            "quantity": 100,
            "unit_price": Decimal("22.99"),
        },
    ]


def get_order_status_history() -> list[dict]:
    """Return seed data for order_status_history table.

    Creates history entries for each order based on their current status.
    Each status transition is recorded with a timestamp reflecting the progression.
    """
    # Status progression for each order type
    status_sequences = {
        "CREATED": ["CREATED"],
        "APPROVED": ["CREATED", "APPROVED"],
        "IN_PRODUCTION": ["CREATED", "APPROVED", "IN_PRODUCTION"],
        "READY_TO_SHIP": ["CREATED", "APPROVED", "IN_PRODUCTION", "READY_TO_SHIP"],
        "SHIPPED": ["CREATED", "APPROVED", "IN_PRODUCTION", "READY_TO_SHIP", "SHIPPED"],
        "DELIVERED": [
            "CREATED",
            "APPROVED",
            "IN_PRODUCTION",
            "READY_TO_SHIP",
            "SHIPPED",
            "DELIVERED",
        ],
        "RETURNED": [
            "CREATED",
            "APPROVED",
            "IN_PRODUCTION",
            "READY_TO_SHIP",
            "SHIPPED",
            "DELIVERED",
            "RETURNED",
        ],
    }

    history = []
    history_idx = 0

    orders = get_orders()
    for order in orders:
        order_id = order["id"]
        status = order["status"]
        created_at = order["created_at"]

        statuses = status_sequences.get(status, ["CREATED"])
        for i, s in enumerate(statuses):
            # Each status transition happens 1 day apart
            transition_time = created_at + timedelta(days=i)
            history.append(
                {
                    "id": ORDER_STATUS_HISTORY_IDS[history_idx],
                    "order_id": order_id,
                    "status": s,
                    "transitioned_at": transition_time,
                }
            )
            history_idx += 1

    return history
