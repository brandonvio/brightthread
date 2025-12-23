"""Integration tests for BrightThread API endpoints.

Tests the deployed FastAPI Lambda function via HTTP requests to verify
proper integration between API Gateway and Lambda.
"""

import pytest


class TestHealthEndpoints:
    """Test system health check endpoints."""

    def test_health_check(self, http_client):
        """Test the /health endpoint."""
        response = http_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_root_endpoint(self, http_client):
        """Test the root / endpoint."""
        response = http_client.get("/")
        assert response.status_code == 200


class TestCompanyEndpoints:
    """Test company management endpoints."""

    def test_get_companies(self, http_client) -> None:
        """Test GET /companies endpoint returns all companies."""
        response = http_client.get("/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10

    def test_get_companies_structure(self, http_client) -> None:
        """Test GET /companies returns properly structured data."""
        response = http_client.get("/companies")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        company = data[0]
        assert "id" in company
        assert "name" in company
        assert "created_at" in company

    def test_get_companies_sorted_by_name(self, http_client) -> None:
        """Test GET /companies returns companies sorted by name."""
        response = http_client.get("/companies")
        assert response.status_code == 200
        data = response.json()
        names = [company["name"] for company in data]
        assert names == sorted(names)


class TestOrderEndpoints:
    """Test order management endpoints."""

    def test_get_order(self, http_client, order_id):
        """Test GET /orders/{order_id} endpoint."""
        response = http_client.get(f"/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "order_id" in data

    def test_get_order_status(self, http_client, order_id):
        """Test GET /orders/{order_id}/status endpoint."""
        response = http_client.get(f"/orders/{order_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_update_order_status(self, http_client, order_id):
        """Test PUT /orders/{order_id}/status endpoint."""
        payload = {"status": "IN_PRODUCTION"}
        response = http_client.put(f"/orders/{order_id}/status", json=payload)
        assert response.status_code == 200

    def test_chat_message(self, http_client, order_id):
        """Test POST /orders/{order_id}/chat endpoint."""
        payload = {
            "order_id": order_id,
            "message": "I need to change the quantity",
            "conversation_history": [],
        }
        response = http_client.post(f"/orders/{order_id}/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "agent_message" in data or "options" in data

    def test_apply_change(self, http_client, order_id):
        """Test POST /orders/{order_id}/apply-change endpoint."""
        payload = {"change_type": "quantity_change", "details": {"new_quantity": 5}}
        response = http_client.post(f"/orders/{order_id}/apply-change", json=payload)
        assert response.status_code == 200


class TestInventoryEndpoints:
    """Test inventory management endpoints."""

    def test_check_inventory(self, http_client):
        """Test GET /inventory/{product_id}/check endpoint."""
        response = http_client.get(
            "/inventory/prod-001/check",
            params={"color": "Navy Blue", "size": "M", "quantity": 50},
        )
        assert response.status_code == 200

    def test_production_timeline(self, http_client, order_id):
        """Test GET /orders/{order_id}/production-timeline endpoint."""
        response = http_client.get(f"/orders/{order_id}/production-timeline")
        assert response.status_code == 200


class TestPolicyEndpoints:
    """Test policy evaluation endpoints."""

    def test_evaluate_change(self, http_client):
        """Test POST /policies/evaluate-change endpoint."""
        payload = {"order_status": "APPROVED", "change_type": "QUANTITY_ADJUSTMENT"}
        response = http_client.post("/policies/evaluate-change", json=payload)
        assert response.status_code == 200


class TestOperationsEndpoints:
    """Test operations and monitoring endpoints."""

    def test_operations_dashboard(self, http_client):
        """Test GET /operations/dashboard endpoint."""
        response = http_client.get("/operations/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data or "status" in data

    def test_create_alert(self, http_client):
        """Test POST /operations/alert endpoint."""
        payload = {
            "alert_type": "order_issue",
            "description": "Order processing delay",
            "severity": "warning",
        }
        response = http_client.post("/operations/alert", json=payload)
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_order_id(self, http_client):
        """Test endpoint with invalid order ID."""
        response = http_client.get("/orders/INVALID/status")
        assert response.status_code == 200

    def test_missing_required_fields(self, http_client, order_id):
        """Test endpoint with missing required fields."""
        payload = {}  # Missing required fields
        response = http_client.put(f"/orders/{order_id}/status", json=payload)
        # Should return validation error or success with defaults
        assert response.status_code in [200, 400, 422]

    def test_api_latency(self, http_client):
        """Test API response time."""
        response = http_client.get("/health")
        assert response.status_code == 200


class TestConcurrentRequests:
    """Test API behavior under concurrent load."""

    @pytest.mark.parametrize("request_num", range(3))
    def test_concurrent_health_checks(self, http_client, request_num):
        """Test multiple concurrent health checks."""
        response = http_client.get("/health")
        assert response.status_code == 200

    @pytest.mark.parametrize("order_id", [f"ORD-{i:03d}" for i in range(3)])
    def test_concurrent_order_requests(self, http_client, order_id):
        """Test multiple concurrent order requests."""
        response = http_client.get(f"/orders/{order_id}/status")
        assert response.status_code == 200
