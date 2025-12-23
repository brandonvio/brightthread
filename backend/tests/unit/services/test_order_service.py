"""Unit tests for OrderService."""

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from db.models import Inventory, Order, OrderLineItem
from services.order_service import (
    InvalidStateTransitionError,
    OrderService,
    OrderValidationError,
)


@pytest.fixture
def mock_order_repo() -> Mock:
    """Create mock order repository."""
    return Mock()


@pytest.fixture
def mock_line_item_repo() -> Mock:
    """Create mock line item repository."""
    return Mock()


@pytest.fixture
def mock_inventory_repo() -> Mock:
    """Create mock inventory repository."""
    return Mock()


@pytest.fixture
def mock_status_history_repo() -> Mock:
    """Create mock status history repository."""
    return Mock()


@pytest.fixture
def mock_user_repo() -> Mock:
    """Create mock user repository."""
    return Mock()


@pytest.fixture
def mock_shipping_repo() -> Mock:
    """Create mock shipping address repository."""
    return Mock()


@pytest.fixture
def mock_artwork_repo() -> Mock:
    """Create mock artwork repository."""
    return Mock()


@pytest.fixture
def order_service(
    mock_order_repo: Mock,
    mock_line_item_repo: Mock,
    mock_inventory_repo: Mock,
    mock_status_history_repo: Mock,
    mock_user_repo: Mock,
    mock_shipping_repo: Mock,
    mock_artwork_repo: Mock,
) -> OrderService:
    """Create OrderService with mocked repositories."""
    return OrderService(
        order_repo=mock_order_repo,
        order_line_item_repo=mock_line_item_repo,
        inventory_repo=mock_inventory_repo,
        status_history_repo=mock_status_history_repo,
        user_repo=mock_user_repo,
        shipping_repo=mock_shipping_repo,
        artwork_repo=mock_artwork_repo,
    )


def test_get_order_success(
    order_service: OrderService, mock_order_repo: Mock, mock_line_item_repo: Mock
) -> None:
    """Test successful order retrieval."""
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    shipping_address_id = uuid.uuid4()

    mock_order = Mock(spec=Order)
    mock_order.id = order_id
    mock_order.user_id = user_id
    mock_order.shipping_address_id = shipping_address_id
    mock_order.artwork_id = None
    mock_order.status = "CREATED"
    mock_order.delivery_date = date.today() + timedelta(days=14)
    mock_order.total_amount = 100.0
    mock_order.created_at = datetime.now(timezone.utc)
    mock_order.updated_at = datetime.now(timezone.utc)

    mock_line_item = Mock(spec=OrderLineItem)
    mock_line_item.id = uuid.uuid4()
    mock_line_item.order_id = order_id
    mock_line_item.inventory_id = uuid.uuid4()
    mock_line_item.quantity = 10
    mock_line_item.unit_price = 10.0

    mock_order_repo.get_by_id.return_value = mock_order
    mock_line_item_repo.get_by_order_id.return_value = [mock_line_item]

    result = order_service.get_order(order_id)

    assert result.id == order_id
    assert len(result.line_items) == 1
    mock_order_repo.get_by_id.assert_called_once_with(order_id)


def test_update_order_status_valid_transition(
    order_service: OrderService, mock_order_repo: Mock, mock_line_item_repo: Mock
) -> None:
    """Test valid order status transition."""
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    shipping_address_id = uuid.uuid4()

    mock_order = Mock(spec=Order)
    mock_order.id = order_id
    mock_order.user_id = user_id
    mock_order.shipping_address_id = shipping_address_id
    mock_order.artwork_id = None
    mock_order.status = "CREATED"
    mock_order.delivery_date = date.today() + timedelta(days=14)
    mock_order.total_amount = 100.0
    mock_order.created_at = datetime.now(timezone.utc)
    mock_order.updated_at = datetime.now(timezone.utc)

    mock_order_repo.get_by_id.return_value = mock_order
    mock_order_repo.update.return_value = mock_order
    mock_line_item_repo.get_by_order_id.return_value = []

    order_service.update_order_status(order_id, "APPROVED")

    assert mock_order.status == "APPROVED"
    mock_order_repo.update.assert_called_once()


def test_update_order_status_invalid_transition(
    order_service: OrderService, mock_order_repo: Mock
) -> None:
    """Test invalid order status transition fails fast."""
    order_id = uuid.uuid4()
    mock_order = Mock(spec=Order)
    mock_order.status = "CREATED"

    mock_order_repo.get_by_id.return_value = mock_order

    with pytest.raises(InvalidStateTransitionError):
        order_service.update_order_status(order_id, "SHIPPED")


def test_create_order_validates_minimum_quantity(order_service: OrderService) -> None:
    """Test order creation validates minimum quantity."""
    user_id = uuid.uuid4()
    shipping_address_id = uuid.uuid4()
    delivery_date = date.today() + timedelta(days=20)

    line_items = [{"inventory_id": uuid.uuid4(), "quantity": 5}]

    with pytest.raises(OrderValidationError):
        order_service.create_order(
            user_id=user_id,
            shipping_address_id=shipping_address_id,
            delivery_date=delivery_date,
            line_items=line_items,
        )


def test_create_order_validates_lead_time(order_service: OrderService) -> None:
    """Test order creation validates minimum lead time."""
    user_id = uuid.uuid4()
    shipping_address_id = uuid.uuid4()
    delivery_date = date.today() + timedelta(days=5)

    line_items = [{"inventory_id": uuid.uuid4(), "quantity": 15}]

    with pytest.raises(OrderValidationError):
        order_service.create_order(
            user_id=user_id,
            shipping_address_id=shipping_address_id,
            delivery_date=delivery_date,
            line_items=line_items,
        )


def test_cancel_order_releases_inventory(
    order_service: OrderService,
    mock_order_repo: Mock,
    mock_line_item_repo: Mock,
    mock_inventory_repo: Mock,
) -> None:
    """Test order cancellation releases inventory."""
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    shipping_address_id = uuid.uuid4()

    mock_order = Mock(spec=Order)
    mock_order.id = order_id
    mock_order.user_id = user_id
    mock_order.shipping_address_id = shipping_address_id
    mock_order.artwork_id = None
    mock_order.status = "CREATED"
    mock_order.delivery_date = date.today() + timedelta(days=14)
    mock_order.total_amount = 100.0
    mock_order.created_at = datetime.now(timezone.utc)
    mock_order.updated_at = datetime.now(timezone.utc)

    mock_inventory = Mock(spec=Inventory)
    mock_inventory.available_qty = 100
    mock_inventory.reserved_qty = 50

    mock_line_item = Mock(spec=OrderLineItem)
    mock_line_item.id = uuid.uuid4()
    mock_line_item.order_id = order_id
    mock_line_item.inventory_id = uuid.uuid4()
    mock_line_item.quantity = 20
    mock_line_item.unit_price = 10.0

    mock_order_repo.get_by_id.return_value = mock_order
    mock_line_item_repo.get_by_order_id.return_value = [mock_line_item]
    mock_inventory_repo.get_by_id.return_value = mock_inventory
    mock_order_repo.update.return_value = mock_order

    order_service.cancel_order(order_id)

    assert mock_inventory.available_qty == 120
    assert mock_inventory.reserved_qty == 30
    assert mock_order.status == "CANCELLED"
