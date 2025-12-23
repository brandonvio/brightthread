"""Pydantic models for catalog (colors/sizes) responses."""

import uuid

from pydantic import BaseModel, ConfigDict


class Color(BaseModel):
    """Color domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    hex_code: str


class Size(BaseModel):
    """Size domain model."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    sort_order: int
