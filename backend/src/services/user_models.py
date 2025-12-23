"""Pydantic models for UserService responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """User domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    email: str
    created_at: datetime
