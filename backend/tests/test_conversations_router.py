"""Unit tests for conversations router."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from agents.services.conversation_service import ConversationService
from agents.services.models import (
    Conversation,
    ConversationListResponse,
    ConversationMessage,
    ConversationSummary,
)
from auth import TokenPayload, decode_bearer_token
from dependencies import get_conversation_service
from main import app


@pytest.fixture
def mock_conversation_service() -> Mock:
    """Create mock conversation service."""
    return Mock(spec=ConversationService)


@pytest.fixture
def mock_auth() -> TokenPayload:
    """Create mock auth payload for testing."""
    return TokenPayload(user_id="user-123")


@pytest.fixture
def client(mock_conversation_service: Mock, mock_auth: TokenPayload) -> TestClient:
    """Create test client with mocked service."""
    app.dependency_overrides[get_conversation_service] = (
        lambda: mock_conversation_service
    )
    app.dependency_overrides[decode_bearer_token] = lambda: mock_auth
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_conversations(
    client: TestClient,
    mock_conversation_service: Mock,
) -> None:
    """Test listing user conversations."""
    user_id = "user-123"
    summaries = [
        ConversationSummary(
            session_id="session-1",
            user_id=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            message_count=5,
            preview="Hello",
        ),
    ]
    response_data = ConversationListResponse(
        conversations=summaries,
        total=1,
    )
    mock_conversation_service.list_conversations.return_value = response_data

    response = client.get("/v1/conversations")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["conversations"]) == 1
    assert data["conversations"][0]["session_id"] == "session-1"


def test_get_conversation_success(
    client: TestClient,
    mock_conversation_service: Mock,
) -> None:
    """Test getting conversation details successfully."""
    user_id = "user-123"
    session_id = "session-abc"
    messages = [
        ConversationMessage(
            role="user",
            content="Hello",
            timestamp=datetime.now(UTC),
        ),
        ConversationMessage(
            role="assistant",
            content="Hi!",
            timestamp=datetime.now(UTC),
        ),
    ]
    conversation = Conversation(
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        messages=messages,
    )
    mock_conversation_service.get_conversation.return_value = conversation

    response = client.get(f"/v1/conversations/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert len(data["messages"]) == 2


def test_get_conversation_not_found(
    mock_conversation_service: Mock,
    mock_auth: TokenPayload,
) -> None:
    """Test getting non-existent conversation fails fast with KeyError."""
    session_id = "invalid-session"
    mock_conversation_service.get_conversation.side_effect = KeyError("Not found")

    # Create client that captures server errors as 500 responses
    app.dependency_overrides[get_conversation_service] = (
        lambda: mock_conversation_service
    )
    app.dependency_overrides[decode_bearer_token] = lambda: mock_auth
    error_client = TestClient(app, raise_server_exceptions=False)

    try:
        response = error_client.get(f"/v1/conversations/{session_id}")

        # Fail fast: KeyError propagates as 500 Internal Server Error
        assert response.status_code == 500
    finally:
        app.dependency_overrides.clear()
