"""Inventory management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import InventoryAvailabilityRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.inventory_repository import InventoryRepository
from services.inventory_models import Inventory, InventoryAvailability
from services.inventory_service import InventoryService

router = APIRouter(prefix="/v1/inventory", tags=["BrightThread Inventory"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class InventoryListResponse(BaseModel):
    """Response for list of inventory items."""

    inventory_items: list[Inventory]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_inventory_service(
    session: Session = Depends(get_db_session),
) -> InventoryService:
    """Create InventoryService with injected dependencies."""
    inventory_repo = InventoryRepository(session)
    return InventoryService(inventory_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=InventoryListResponse)
def list_inventory(
    auth: AuthenticatedUser,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryListResponse:
    """List all inventory records."""
    logger.info("GET /v1/inventory")

    inventory_items = inventory_service.get_all_inventory()
    return InventoryListResponse(
        inventory_items=inventory_items, total=len(inventory_items)
    )


@router.get("/{inventory_id}", response_model=Inventory)
def get_inventory(
    inventory_id: str,
    auth: AuthenticatedUser,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> Inventory:
    """Get inventory record by ID."""
    logger.info(f"GET /v1/inventory/{inventory_id}")

    inventory_uuid = uuid.UUID(inventory_id)
    return inventory_service.get_inventory_by_id(inventory_uuid)


@router.post("/check-availability", response_model=InventoryAvailability)
def check_availability(
    request: InventoryAvailabilityRequest,
    auth: AuthenticatedUser,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryAvailability:
    """Check inventory availability."""
    logger.info("POST /v1/inventory/check-availability")

    return inventory_service.check_availability(
        product_id=request.product_id,
        color_id=request.color_id,
        size_id=request.size_id,
        quantity=request.quantity,
    )


@router.get("/product/{product_id}", response_model=InventoryListResponse)
def get_inventory_by_product(
    product_id: str,
    auth: AuthenticatedUser,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryListResponse:
    """Get all inventory records for a product."""
    logger.info(f"GET /v1/inventory/product/{product_id}")

    product_uuid = uuid.UUID(product_id)
    inventory_items = inventory_service.get_inventory_by_product(product_uuid)
    return InventoryListResponse(
        inventory_items=inventory_items, total=len(inventory_items)
    )
