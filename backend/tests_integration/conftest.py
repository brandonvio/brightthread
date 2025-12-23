"""Fixtures for integration tests.

These tests hit a real deployed API and are skipped unless
RUN_INTEGRATION_TESTS=true is set in the environment.
"""

import os

import httpx
import pytest


# Skip all tests in this directory unless RUN_INTEGRATION_TESTS is set
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require deployed API)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """Skip integration tests unless RUN_INTEGRATION_TESTS is set."""
    if os.getenv("RUN_INTEGRATION_TESTS", "").lower() != "true":
        skip_integration = pytest.mark.skip(
            reason="Integration tests skipped. Set RUN_INTEGRATION_TESTS=true to run."
        )
        for item in items:
            if "tests_integration" in str(item.fspath):
                item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def api_endpoint() -> str:
    """Get the deployed API endpoint from environment variable or use default.

    Returns:
        str: Base URL of the deployed API (e.g., https://api.brightthread.design)
    """
    endpoint = os.getenv("API_ENDPOINT", "https://api.brightthread.design")
    return endpoint.rstrip("/")


@pytest.fixture
def http_client(api_endpoint):
    """Create an HTTP client for API requests.

    Args:
        api_endpoint: The base API endpoint

    Yields:
        httpx.Client: HTTP client configured for the API
    """
    with httpx.Client(base_url=api_endpoint, timeout=30.0) as client:
        yield client


@pytest.fixture
def async_http_client(api_endpoint):
    """Create an async HTTP client for API requests.

    Args:
        api_endpoint: The base API endpoint

    Yields:
        httpx.AsyncClient: Async HTTP client configured for the API
    """

    async def _async_client():
        async with httpx.AsyncClient(base_url=api_endpoint, timeout=30.0) as client:
            yield client

    return _async_client()


@pytest.fixture
def order_id():
    """Sample order ID for testing.

    Returns:
        str: Order ID
    """
    return "ORD-001"


@pytest.fixture
def customer_request():
    """Sample customer request for testing.

    Returns:
        dict: Customer request data
    """
    return {
        "customer_id": "CUST-123",
        "order_id": "ORD-001",
        "message": "I need to change the quantity",
        "requested_changes": [
            {"change_type": "quantity_change", "details": {"new_quantity": 5}}
        ],
    }
