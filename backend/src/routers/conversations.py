"""Conversation management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from agents.services.conversation_service import ConversationService
from agents.services.models import Conversation, ConversationListResponse
from auth import AuthenticatedUser
from dependencies import get_conversation_service

router = APIRouter(prefix="/v1/conversations", tags=["Conversations"])


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    auth: AuthenticatedUser,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ConversationListResponse:
    """List all conversations for the authenticated user.

    Args:
        auth: Authenticated user from bearer token
        conversation_service: Injected conversation service

    Returns:
        ConversationListResponse with summaries
    """
    user_id = auth.user_id
    logger.info(f"GET /v1/conversations - user_id: {user_id}")
    conversations = conversation_service.list_conversations(user_id)
    logger.info(f"Retrieved {conversations.total} conversations")
    return conversations


@router.get("/{session_id}", response_model=Conversation)
def get_conversation(
    session_id: str,
    auth: AuthenticatedUser,
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> Conversation:
    """Get conversation details with full message history.

    Args:
        session_id: Unique session identifier
        auth: Authenticated user from bearer token
        conversation_service: Injected conversation service

    Returns:
        Conversation with all messages

    Raises:
        HTTPException: 404 if conversation not found
    """
    user_id = auth.user_id
    logger.info(f"GET /v1/conversations/{session_id} - user_id: {user_id}")
    conversation = conversation_service.get_conversation(user_id, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(
        f"Retrieved conversation {session_id} with {len(conversation.messages)} messages"
    )
    return conversation
