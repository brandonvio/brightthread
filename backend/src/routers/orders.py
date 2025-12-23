"""Order management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import (
    CreateOrderRequest,
    UpdateOrderRequest,
    UpdateOrderStatusRequest,
)
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.artwork_repository import ArtworkRepository
from repositories.inventory_repository import InventoryRepository
from repositories.order_line_item_repository import OrderLineItemRepository
from repositories.order_repository import OrderRepository
from repositories.order_status_history_repository import OrderStatusHistoryRepository
from repositories.shipping_address_repository import ShippingAddressRepository
from repositories.user_repository import UserRepository
from services.order_models import (
    EnrichedOrder,
    Order,
    OrderStatusHistory,
    OrderSummary,
)
from services.order_service import OrderService

router = APIRouter(prefix="/v1/orders", tags=["BrightThread Orders"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class OrderListResponse(BaseModel):
    """Response for list of orders."""

    orders: list[OrderSummary]
    total: int


class OrderStatusHistoryListResponse(BaseModel):
    """Response for list of order status history entries."""

    history: list[OrderStatusHistory]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_order_service(session: Session = Depends(get_db_session)) -> OrderService:
    """Create OrderService with injected dependencies."""
    return OrderService(
        order_repo=OrderRepository(session),
        order_line_item_repo=OrderLineItemRepository(session),
        inventory_repo=InventoryRepository(session),
        status_history_repo=OrderStatusHistoryRepository(session),
        user_repo=UserRepository(session),
        shipping_repo=ShippingAddressRepository(session),
        artwork_repo=ArtworkRepository(session),
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=OrderListResponse)
def list_orders(
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    """List all orders for the authenticated user."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"GET /v1/orders - user_id: {user_id}")

    orders = order_service.get_orders_by_user(user_id)
    return OrderListResponse(orders=orders, total=len(orders))


@router.get("/{order_id}", response_model=EnrichedOrder)
def get_order(
    order_id: str,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> EnrichedOrder:
    """Get order details with all related information."""
    logger.info(f"GET /v1/orders/{order_id}")

    order_uuid = uuid.UUID(order_id)
    return order_service.get_enriched_order(order_uuid)


@router.get("/{order_id}/history", response_model=OrderStatusHistoryListResponse)
def get_order_status_history(
    order_id: str,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderStatusHistoryListResponse:
    """Get status history for an order."""
    logger.info(f"GET /v1/orders/{order_id}/history")

    order_uuid = uuid.UUID(order_id)
    history = order_service.get_status_history(order_uuid)
    return OrderStatusHistoryListResponse(history=history, total=len(history))


@router.post("", response_model=Order, status_code=201)
def create_order(
    request: CreateOrderRequest,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Create a new order."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"POST /v1/orders - user_id: {user_id}")

    line_items = [
        {"inventory_id": item.inventory_id, "quantity": item.quantity}
        for item in request.line_items
    ]

    return order_service.create_order(
        user_id=user_id,
        shipping_address_id=request.shipping_address_id,
        delivery_date=request.delivery_date,
        line_items=line_items,
        artwork_id=request.artwork_id,
    )


@router.patch("/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: str,
    request: UpdateOrderStatusRequest,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Update order status."""
    logger.info(f"PATCH /v1/orders/{order_id}/status")

    order_uuid = uuid.UUID(order_id)
    return order_service.update_order_status(order_uuid, request.status)


@router.patch("/{order_id}", response_model=Order)
def update_order(
    order_id: str,
    request: UpdateOrderRequest,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Update order details."""
    logger.info(f"PATCH /v1/orders/{order_id}")

    order_uuid = uuid.UUID(order_id)
    return order_service.modify_order(
        order_id=order_uuid,
        shipping_address_id=request.shipping_address_id,
        artwork_id=request.artwork_id,
        delivery_date=request.delivery_date,
    )


@router.delete("/{order_id}", response_model=Order)
def cancel_order(
    order_id: str,
    auth: AuthenticatedUser,
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    """Cancel an order."""
    logger.info(f"DELETE /v1/orders/{order_id}")

    order_uuid = uuid.UUID(order_id)
    return order_service.cancel_order(order_uuid)
