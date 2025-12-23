"""Pydantic models for ProductService responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    """Product domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    supplier_id: uuid.UUID
    sku: str
    name: str
    description: str | None
    base_price: float
    created_at: datetime
