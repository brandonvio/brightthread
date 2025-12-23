"""Unit tests for agent router endpoints."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from agents.cx_order_support_agent import CXOrderSupportAgent
from agents.services.conversation_service import ConversationService
from auth import TokenPayload, decode_bearer_token
from dependencies import get_conversation_service, get_cx_agent
from main import app


@pytest.fixture
def mock_agent() -> Mock:
    """Mock CXOrderSupportAgent for testing.

    Returns:
        Mock agent instance
    """
    mock = Mock(spec=CXOrderSupportAgent)
    mock.process_message.return_value = "I'm here to help with your order."
    return mock


@pytest.fixture
def mock_conversation_service() -> Mock:
    """Mock ConversationService for testing.

    Returns:
        Mock conversation service instance
    """
    mock = Mock(spec=ConversationService)
    return mock


@pytest.fixture
def mock_auth() -> TokenPayload:
    """Create mock auth payload for testing.

    Returns:
        TokenPayload with test user
    """
    return TokenPayload(user_id="default-user")


@pytest.fixture
def client(
    mock_agent: Mock, mock_conversation_service: Mock, mock_auth: TokenPayload
) -> TestClient:
    """Create test client with mocked dependencies.

    Args:
        mock_agent: Mocked agent instance
        mock_conversation_service: Mocked conversation service
        mock_auth: Mocked auth payload

    Returns:
        FastAPI TestClient
    """
    app.dependency_overrides[get_cx_agent] = lambda: mock_agent
    app.dependency_overrides[get_conversation_service] = (
        lambda: mock_conversation_service
    )
    app.dependency_overrides[decode_bearer_token] = lambda: mock_auth
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_chat_completions_endpoint_success(
    client: TestClient, mock_agent: Mock, mock_conversation_service: Mock
) -> None:
    """Test chat completions endpoint processes request successfully."""
    request_data = {
        "model": "claude-haiku-4.5",
        "messages": [{"role": "user", "content": "Hello, I need help"}],
        "temperature": 0.7,
        "max_tokens": 512,
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert data["object"] == "chat.completion"
    assert data["model"] == "claude-haiku-4.5"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert (
        data["choices"][0]["message"]["content"] == "I'm here to help with your order."
    )
    assert data["choices"][0]["finish_reason"] == "stop"
    assert data["usage"]["total_tokens"] > 0
    assert "session_id" in data

    # Verify new session was created
    mock_conversation_service.create_conversation.assert_called_once()
    # Verify agent was called with session_id
    assert mock_agent.process_message.call_count == 1


def test_chat_completions_uses_last_user_message(
    client: TestClient, mock_agent: Mock
) -> None:
    """Test endpoint extracts last user message from conversation."""
    request_data = {
        "model": "claude-haiku-4.5",
        "messages": [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
        ],
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)

    assert response.status_code == 200
    # Verify last user message was used
    call_args = mock_agent.process_message.call_args[0]
    assert call_args[0] == "Second message"


def test_chat_completions_response_format(client: TestClient) -> None:
    """Test response matches OpenAI format specification."""
    request_data = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Test"}],
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)
    data = response.json()

    assert "id" in data
    assert data["id"].startswith("chatcmpl-")
    assert "created" in data
    assert isinstance(data["created"], int)
    assert "model" in data
    assert "choices" in data
    assert "usage" in data
    assert "prompt_tokens" in data["usage"]
    assert "completion_tokens" in data["usage"]
    assert "total_tokens" in data["usage"]
    assert "session_id" in data


def test_chat_completions_validates_request(client: TestClient) -> None:
    """Test endpoint validates request schema."""
    invalid_request = {
        "messages": "not a list",
    }

    response = client.post("/v1/chat/completions", json=invalid_request)

    assert response.status_code == 422


def test_chat_completions_fails_without_user_message(client: TestClient) -> None:
    """Test endpoint fails fast when no user messages provided."""
    request_data = {
        "model": "test-model",
        "messages": [{"role": "system", "content": "System prompt only"}],
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    # Should raise IndexError from router - fail fast behavior
    with pytest.raises(IndexError):
        client.post("/v1/chat/completions", json=request_data)


def test_chat_completions_creates_new_session(
    client: TestClient, mock_conversation_service: Mock
) -> None:
    """Test endpoint creates new session when session_id not provided."""
    request_data = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"].startswith("session-")
    mock_conversation_service.create_conversation.assert_called_once()


def test_chat_completions_continues_existing_session(
    client: TestClient, mock_conversation_service: Mock, mock_agent: Mock
) -> None:
    """Test endpoint continues existing session when session_id provided."""
    session_id = "existing-session-123"
    user_id = "default-user"
    request_data = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Continue conversation"}],
        "session_id": session_id,
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    mock_conversation_service.get_conversation.assert_called_once_with(
        user_id, session_id
    )
    # Verify agent was called with provided session_id
    call_args = mock_agent.process_message.call_args[0]
    assert call_args[1] == session_id


def test_chat_completions_fails_with_invalid_session(
    client: TestClient, mock_conversation_service: Mock
) -> None:
    """Test endpoint returns 404 for invalid session_id."""
    mock_conversation_service.get_conversation.side_effect = KeyError("Not found")
    request_data = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Test"}],
        "session_id": "invalid-session",
        "order_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/v1/chat/completions", json=request_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
