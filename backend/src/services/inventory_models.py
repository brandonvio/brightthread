"""Pydantic models for InventoryService responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Inventory(BaseModel):
    """Inventory domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    color_id: uuid.UUID
    size_id: uuid.UUID
    available_qty: int
    reserved_qty: int
    updated_at: datetime


class EnrichedInventory(BaseModel):
    """Inventory with product, color, and size details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    color_id: uuid.UUID
    size_id: uuid.UUID
    available_qty: int
    reserved_qty: int
    updated_at: datetime
    # Enriched fields
    product_name: str
    product_sku: str
    color_name: str
    color_hex: str
    size_name: str
    size_code: str


class InventoryAvailability(BaseModel):
    """Inventory availability check result."""

    model_config = ConfigDict(from_attributes=True)

    available: bool
    available_qty: int
    reserved_qty: int
