"""Shipping address management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import CreateShippingAddressRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.shipping_address_repository import ShippingAddressRepository
from services.shipping_models import ShippingAddress
from services.shipping_service import ShippingService

router = APIRouter(prefix="/v1/shipping", tags=["BrightThread Shipping"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class ShippingAddressListResponse(BaseModel):
    """Response for list of shipping addresses."""

    addresses: list[ShippingAddress]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_shipping_service(
    session: Session = Depends(get_db_session),
) -> ShippingService:
    """Create ShippingService with injected dependencies."""
    shipping_repo = ShippingAddressRepository(session)
    return ShippingService(shipping_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=ShippingAddressListResponse)
def list_addresses(
    auth: AuthenticatedUser,
    shipping_service: ShippingService = Depends(get_shipping_service),
) -> ShippingAddressListResponse:
    """List all shipping addresses for the authenticated user."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"GET /v1/shipping - user_id: {user_id}")

    addresses = shipping_service.list_user_addresses(user_id)
    return ShippingAddressListResponse(addresses=addresses, total=len(addresses))


@router.get("/default", response_model=ShippingAddress)
def get_default_address(
    auth: AuthenticatedUser,
    shipping_service: ShippingService = Depends(get_shipping_service),
) -> ShippingAddress:
    """Get the default shipping address for the authenticated user."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"GET /v1/shipping/default - user_id: {user_id}")

    return shipping_service.get_default_address(user_id)


@router.get("/{address_id}", response_model=ShippingAddress)
def get_address(
    address_id: str,
    auth: AuthenticatedUser,
    shipping_service: ShippingService = Depends(get_shipping_service),
) -> ShippingAddress:
    """Get shipping address by ID."""
    logger.info(f"GET /v1/shipping/{address_id}")

    address_uuid = uuid.UUID(address_id)
    return shipping_service.get_address(address_uuid)


@router.post("", response_model=ShippingAddress, status_code=201)
def create_address(
    request: CreateShippingAddressRequest,
    auth: AuthenticatedUser,
    shipping_service: ShippingService = Depends(get_shipping_service),
) -> ShippingAddress:
    """Create a new shipping address."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"POST /v1/shipping - user_id: {user_id}")

    return shipping_service.create_address(
        user_id=user_id,
        label=request.label,
        street_address=request.street_address,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        country=request.country,
        is_default=request.is_default,
    )


@router.patch("/{address_id}/set-default", response_model=ShippingAddress)
def set_default_address(
    address_id: str,
    auth: AuthenticatedUser,
    shipping_service: ShippingService = Depends(get_shipping_service),
) -> ShippingAddress:
    """Set an address as the default."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"PATCH /v1/shipping/{address_id}/set-default")

    address_uuid = uuid.UUID(address_id)
    return shipping_service.set_default(address_uuid, user_id)
