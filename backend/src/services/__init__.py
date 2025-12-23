"""Services for BrightThread Order Support Agent."""

from .artwork_service import ArtworkService
from .company_service import CompanyService
from .inventory_service import InsufficientInventoryError, InventoryService
from .order_service import (
    InvalidOrderModificationError,
    InvalidStateTransitionError,
    OrderService,
    OrderValidationError,
)
from .order_service import InsufficientInventoryError as OrderInsufficientInventoryError
from .product_service import ProductService
from .shipping_service import ShippingService
from .user_service import UserService

# Re-export models for convenience
from .artwork_models import Artwork
from .catalog_models import Color, Size
from .company_models import Company
from .inventory_models import EnrichedInventory, Inventory, InventoryAvailability
from .order_models import (
    EnrichedOrder,
    EnrichedOrderLineItem,
    Order,
    OrderLineItem,
    OrderStatusHistory,
    OrderSummary,
)
from .product_models import Product
from .shipping_models import ShippingAddress
from .user_models import User

__all__ = [
    # Services
    "ArtworkService",
    "CompanyService",
    "InsufficientInventoryError",
    "InvalidOrderModificationError",
    "InvalidStateTransitionError",
    "InventoryService",
    "OrderInsufficientInventoryError",
    "OrderService",
    "OrderValidationError",
    "ProductService",
    "ShippingService",
    "UserService",
    # Models
    "Artwork",
    "Color",
    "Company",
    "EnrichedInventory",
    "EnrichedOrder",
    "EnrichedOrderLineItem",
    "Inventory",
    "InventoryAvailability",
    "Order",
    "OrderLineItem",
    "OrderStatusHistory",
    "OrderSummary",
    "Product",
    "ShippingAddress",
    "Size",
    "User",
]
