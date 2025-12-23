"""Conversation service for business logic."""

from datetime import UTC, datetime

from agents.services.models import (
    Conversation,
    ConversationListResponse,
    ConversationSummary,
)
from repositories.conversation_repo import ConversationRepository


class ConversationService:
    """Service layer for conversation operations."""

    def __init__(self, repository: ConversationRepository) -> None:
        """Initialize service with repository dependency.

        Args:
            repository: ConversationRepository for data access
        """
        self._repository = repository

    def create_conversation(self, session_id: str, user_id: str) -> ConversationSummary:
        """Create new conversation session.

        Args:
            session_id: Unique session identifier
            user_id: User who owns the conversation

        Returns:
            ConversationSummary for the new conversation
        """
        return self._repository.create(session_id, user_id)

    def list_conversations(self, user_id: str) -> ConversationListResponse:
        """List all conversations for a user.

        Args:
            user_id: User identifier

        Returns:
            ConversationListResponse with summaries and total count
        """
        summaries = self._repository.list_by_user_id(user_id)
        return ConversationListResponse(
            conversations=summaries,
            total=len(summaries),
        )

    def get_conversation(self, user_id: str, session_id: str) -> Conversation | None:
        """Get conversation with full message history.

        Args:
            user_id: User who owns the conversation
            session_id: Unique session identifier

        Returns:
            Conversation with all messages, or None if not found
        """
        return self._repository.get_by_session_id(user_id, session_id)

    def update_after_message(
        self, user_id: str, session_id: str, role: str, content: str
    ) -> None:
        """Update conversation metadata after new message.

        Args:
            user_id: User who owns the conversation
            session_id: Session to update
            role: Message role (user or assistant)
            content: Message content
        """
        timestamp = datetime.now(UTC)
        self._repository.update_metadata(user_id, session_id, role, content, timestamp)
