"""Pydantic models for API requests.

Response models are defined in the service layer (services/*_models.py).
List response wrappers are defined in routers where needed.
"""

import uuid
from datetime import date

from pydantic import BaseModel


# =============================================================================
# User Requests
# =============================================================================


class CreateUserRequest(BaseModel):
    """Request to create a new user."""

    company_id: uuid.UUID
    email: str
    password: str


# =============================================================================
# Company Requests
# =============================================================================


class CreateCompanyRequest(BaseModel):
    """Request to create a new company."""

    name: str


# =============================================================================
# Product Requests
# =============================================================================


class CreateProductRequest(BaseModel):
    """Request to create a new product."""

    supplier_id: uuid.UUID
    sku: str
    name: str
    description: str | None = None
    base_price: float


# =============================================================================
# Artwork Requests
# =============================================================================


class CreateArtworkRequest(BaseModel):
    """Request to create a new artwork."""

    name: str
    file_url: str
    file_type: str
    width_px: int
    height_px: int


class UpdateArtworkRequest(BaseModel):
    """Request to update artwork."""

    is_active: bool


# =============================================================================
# Shipping Address Requests
# =============================================================================


class CreateShippingAddressRequest(BaseModel):
    """Request to create a new shipping address."""

    label: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False


class UpdateShippingAddressRequest(BaseModel):
    """Request to update shipping address."""

    label: str | None = None
    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


# =============================================================================
# Order Requests
# =============================================================================


class CreateOrderLineItemRequest(BaseModel):
    """Request to create an order line item."""

    inventory_id: uuid.UUID
    quantity: int


class CreateOrderRequest(BaseModel):
    """Request to create a new order."""

    shipping_address_id: uuid.UUID
    artwork_id: uuid.UUID | None = None
    delivery_date: date
    line_items: list[CreateOrderLineItemRequest]


class UpdateOrderStatusRequest(BaseModel):
    """Request to update order status."""

    status: str


class UpdateOrderRequest(BaseModel):
    """Request to update order details."""

    shipping_address_id: uuid.UUID | None = None
    artwork_id: uuid.UUID | None = None
    delivery_date: date | None = None


# =============================================================================
# Inventory Requests
# =============================================================================


class InventoryAvailabilityRequest(BaseModel):
    """Request to check inventory availability."""

    product_id: uuid.UUID
    color_id: uuid.UUID
    size_id: uuid.UUID
    quantity: int
