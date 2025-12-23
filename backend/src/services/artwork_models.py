"""Pydantic models for ArtworkService responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Artwork(BaseModel):
    """Artwork domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_by_user_id: uuid.UUID
    name: str
    file_url: str
    file_type: str
    width_px: int
    height_px: int
    is_active: bool
    created_at: datetime
