"""Unit tests for OrderTools."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import Mock

import pytest

from agents.tools.order_tools import OrderTools
from services.order_models import EnrichedOrder, EnrichedOrderLineItem
from services.shipping_models import ShippingAddress


def _create_shipping_address() -> ShippingAddress:
    """Create a ShippingAddress for testing."""
    return ShippingAddress(
        id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        label="Home",
        street_address="123 Main St",
        city="Test City",
        state="TS",
        postal_code="12345",
        country="US",
        is_default=True,
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )


def _create_enriched_order(
    order_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> EnrichedOrder:
    """Create an EnrichedOrder Pydantic model for testing."""
    return EnrichedOrder(
        id=order_id,
        user_id=user_id or uuid.uuid4(),
        shipping_address_id=uuid.uuid4(),
        artwork_id=None,
        status="CREATED",
        delivery_date=date(2025, 1, 15),
        total_amount=100.0,
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        line_items=[],
        user_email="test@example.com",
        shipping_address=_create_shipping_address(),
        artwork=None,
    )


def _create_enriched_order_with_line_items(
    order_id: uuid.UUID, item_id: uuid.UUID, quantity: int
) -> EnrichedOrder:
    """Create an EnrichedOrder with line items for testing."""
    line_item = EnrichedOrderLineItem(
        id=item_id,
        order_id=order_id,
        inventory_id=uuid.uuid4(),
        quantity=quantity,
        unit_price=10.0,
        product_name="Test Product",
        product_sku="TEST-SKU",
        size="Medium",
        color="Blue",
        color_hex="#0000FF",
    )
    return EnrichedOrder(
        id=order_id,
        user_id=uuid.uuid4(),
        shipping_address_id=uuid.uuid4(),
        artwork_id=None,
        status="CREATED",
        delivery_date=date(2025, 1, 15),
        total_amount=100.0,
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        line_items=[line_item],
        user_email="test@example.com",
        shipping_address=_create_shipping_address(),
        artwork=None,
    )


def test_get_order_details_success() -> None:
    """Test successful order details retrieval."""
    mock_order_service = Mock()
    order_id = uuid.uuid4()
    item_id = uuid.uuid4()

    mock_order = _create_enriched_order_with_line_items(order_id, item_id, 10)
    mock_order_service.get_enriched_order.return_value = mock_order

    order_tools = OrderTools(order_service=mock_order_service)

    result = order_tools.get_order_details(str(order_id))

    assert result["id"] == str(order_id)
    assert result["status"] == "CREATED"
    assert len(result["line_items"]) == 1
    assert result["line_items"][0]["quantity"] == 10
    mock_order_service.get_enriched_order.assert_called_once_with(order_id)


def test_get_order_details_uuid_conversion() -> None:
    """Test that string order_id is converted to UUID correctly."""
    mock_order_service = Mock()
    order_id_str = "550e8400-e29b-41d4-a716-446655440000"
    order_id_uuid = uuid.UUID(order_id_str)

    mock_order = _create_enriched_order(order_id_uuid)
    mock_order_service.get_enriched_order.return_value = mock_order

    order_tools = OrderTools(order_service=mock_order_service)

    result = order_tools.get_order_details(order_id_str)

    assert result["id"] == order_id_str
    assert result["line_items"] == []
    mock_order_service.get_enriched_order.assert_called_once_with(order_id_uuid)


def test_get_order_details_invalid_uuid() -> None:
    """Test that invalid UUID string raises ValueError."""
    mock_order_service = Mock()
    order_tools = OrderTools(order_service=mock_order_service)

    with pytest.raises(ValueError):
        order_tools.get_order_details("invalid-uuid")
