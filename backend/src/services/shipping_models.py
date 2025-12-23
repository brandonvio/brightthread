"""Pydantic models for ShippingService responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShippingAddress(BaseModel):
    """Shipping address domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by_user_id: uuid.UUID
    label: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    created_at: datetime
