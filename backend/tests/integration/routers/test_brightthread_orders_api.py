"""Integration tests for BrightThread Orders API."""

import base64
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock

from fastapi.testclient import TestClient

from main import app
from routers.orders import get_order_service
from services.order_models import (
    EnrichedOrder,
    Order,
)
from services.shipping_models import ShippingAddress

client = TestClient(app)


def _make_token(user_id: str) -> str:
    """Create a valid auth token for testing."""
    payload = {"user_id": user_id}
    return base64.b64encode(json.dumps(payload).encode()).decode()


def _create_mock_order(
    order_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    status: str = "CREATED",
) -> Order:
    """Create a mock order object."""
    return Order(
        id=order_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        shipping_address_id=uuid.uuid4(),
        artwork_id=None,
        status=status,
        delivery_date=date.today() + timedelta(days=20),
        total_amount=100.00,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        line_items=[],
    )


def _create_mock_enriched_order(
    order_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    status: str = "CREATED",
) -> EnrichedOrder:
    """Create a mock enriched order object."""
    shipping_address_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)

    return EnrichedOrder(
        id=order_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        shipping_address_id=shipping_address_id,
        artwork_id=None,
        status=status,
        delivery_date=date.today() + timedelta(days=20),
        total_amount=100.00,
        created_at=created_at,
        updated_at=created_at,
        line_items=[],
        user_email="test@example.com",
        shipping_address=ShippingAddress(
            id=shipping_address_id,
            created_by_user_id=user_id or uuid.uuid4(),
            label="Home",
            street_address="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US",
            is_default=True,
            created_at=created_at,
        ),
        artwork=None,
    )


def test_list_orders_returns_200() -> None:
    """Test list orders endpoint returns 200."""
    user_id = uuid.uuid4()

    mock_service = Mock()
    mock_service.get_orders_by_user.return_value = []

    app.dependency_overrides[get_order_service] = lambda: mock_service

    try:
        token = _make_token(str(user_id))
        response = client.get(
            "/v1/orders",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert "orders" in response.json()
        assert "total" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_create_order_returns_201() -> None:
    """Test create order endpoint returns 201."""
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_order = _create_mock_order(order_id=order_id, user_id=user_id)

    mock_service = Mock()
    mock_service.create_order.return_value = mock_order

    app.dependency_overrides[get_order_service] = lambda: mock_service

    try:
        token = _make_token(str(user_id))
        request_data = {
            "shipping_address_id": str(uuid.uuid4()),
            "delivery_date": str(date.today() + timedelta(days=20)),
            "line_items": [{"inventory_id": str(uuid.uuid4()), "quantity": 15}],
        }

        response = client.post(
            "/v1/orders",
            json=request_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["status"] == "CREATED"
    finally:
        app.dependency_overrides.clear()


def test_get_order_by_id_returns_200() -> None:
    """Test get order by ID endpoint returns 200."""
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_order = _create_mock_enriched_order(order_id=order_id, user_id=user_id)

    mock_service = Mock()
    mock_service.get_enriched_order.return_value = mock_order

    app.dependency_overrides[get_order_service] = lambda: mock_service

    try:
        token = _make_token(str(user_id))
        response = client.get(
            f"/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "CREATED"
    finally:
        app.dependency_overrides.clear()
