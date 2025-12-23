"""Unit tests for conversation service."""

import sys
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

sys.path.insert(0, "src")

from agents.services.models import (
    Conversation,
    ConversationMessage,
    ConversationSummary,
)
from repositories.conversation_repo import ConversationRepository
from agents.services.conversation_service import ConversationService


@pytest.fixture
def mock_conversation_repo() -> Mock:
    """Create mock conversation repository."""
    return Mock(spec=ConversationRepository)


@pytest.fixture
def conversation_service(mock_conversation_repo: Mock) -> ConversationService:
    """Create conversation service with mocked repository."""
    return ConversationService(mock_conversation_repo)


def test_create_conversation(
    conversation_service: ConversationService,
    mock_conversation_repo: Mock,
) -> None:
    """Test creating new conversation."""
    session_id = "test-session-123"
    user_id = "user-456"

    expected_summary = ConversationSummary(
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        message_count=0,
        preview="",
    )
    mock_conversation_repo.create.return_value = expected_summary

    result = conversation_service.create_conversation(session_id, user_id)

    mock_conversation_repo.create.assert_called_once_with(session_id, user_id)
    assert result == expected_summary


def test_list_conversations(
    conversation_service: ConversationService,
    mock_conversation_repo: Mock,
) -> None:
    """Test listing user conversations."""
    user_id = "user-789"
    summaries = [
        ConversationSummary(
            session_id="session-1",
            user_id=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            message_count=5,
            preview="Hello, I need help",
        ),
        ConversationSummary(
            session_id="session-2",
            user_id=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            message_count=3,
            preview="Can I change my order?",
        ),
    ]
    mock_conversation_repo.list_by_user_id.return_value = summaries

    result = conversation_service.list_conversations(user_id)

    mock_conversation_repo.list_by_user_id.assert_called_once_with(user_id)
    assert result.conversations == summaries
    assert result.total == 2


def test_get_conversation(
    conversation_service: ConversationService,
    mock_conversation_repo: Mock,
) -> None:
    """Test getting conversation with full history."""
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
            content="Hi there!",
            timestamp=datetime.now(UTC),
        ),
    ]
    expected_conversation = Conversation(
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        messages=messages,
    )
    mock_conversation_repo.get_by_session_id.return_value = expected_conversation

    result = conversation_service.get_conversation(user_id, session_id)

    mock_conversation_repo.get_by_session_id.assert_called_once_with(
        user_id, session_id
    )
    assert result == expected_conversation


def test_update_after_message(
    conversation_service: ConversationService,
    mock_conversation_repo: Mock,
) -> None:
    """Test updating conversation metadata after message."""
    user_id = "user-123"
    session_id = "session-xyz"
    role = "user"
    content = "New message content"

    conversation_service.update_after_message(user_id, session_id, role, content)

    mock_conversation_repo.update_metadata.assert_called_once()
    args = mock_conversation_repo.update_metadata.call_args[0]
    assert args[0] == user_id
    assert args[1] == session_id
    assert args[2] == role
    assert args[3] == content
    assert isinstance(args[4], datetime)


def test_service_requires_repository() -> None:
    """Test that service requires repository dependency."""
    with pytest.raises(TypeError):
        ConversationService()  # type: ignore
