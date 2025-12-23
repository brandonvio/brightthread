"""Pydantic models for OrderService responses."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from services.artwork_models import Artwork
from services.shipping_models import ShippingAddress


class OrderLineItem(BaseModel):
    """Order line item domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    inventory_id: uuid.UUID
    quantity: int
    unit_price: float


class EnrichedOrderLineItem(BaseModel):
    """Order line item with product/size/color details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    inventory_id: uuid.UUID
    quantity: int
    unit_price: float
    # Enriched fields
    product_name: str
    product_sku: str
    size: str
    color: str
    color_hex: str


class Order(BaseModel):
    """Order domain model with line items."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    shipping_address_id: uuid.UUID
    artwork_id: uuid.UUID | None
    status: str
    delivery_date: date
    total_amount: float
    created_at: datetime
    updated_at: datetime
    line_items: list[OrderLineItem] = Field(default_factory=list)


class EnrichedOrder(BaseModel):
    """Order with all enriched details for display."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    shipping_address_id: uuid.UUID
    artwork_id: uuid.UUID | None
    status: str
    delivery_date: date
    total_amount: float
    created_at: datetime
    updated_at: datetime
    line_items: list[EnrichedOrderLineItem] = Field(default_factory=list)
    # Enriched fields
    user_email: str
    shipping_address: ShippingAddress
    artwork: Artwork | None = None


class OrderSummary(BaseModel):
    """Order summary with enriched line items for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    shipping_address_id: uuid.UUID
    artwork_id: uuid.UUID | None
    status: str
    delivery_date: date
    total_amount: float
    created_at: datetime
    updated_at: datetime
    line_items: list[EnrichedOrderLineItem] = Field(default_factory=list)


class OrderStatusHistory(BaseModel):
    """Order status history entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    status: str
    transitioned_at: datetime
