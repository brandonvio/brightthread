"""OpenAI-compatible agent endpoint."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from agents.cx_order_support_agent import CXOrderSupportAgent
from agents.services.conversation_service import ConversationService
from agents.services.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    MessageRole,
)
from auth import AuthenticatedUser
from dependencies import get_conversation_service, get_cx_agent

router = APIRouter(prefix="/v1/chat", tags=["Agent"])


@router.post("/completions", response_model=ChatCompletionResponse)
def chat_completions(
    request: ChatCompletionRequest,
    auth: AuthenticatedUser,
    agent: CXOrderSupportAgent = Depends(get_cx_agent),
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> ChatCompletionResponse:
    """OpenAI-compatible chat completions endpoint.

    Args:
        request: Chat completion request with messages
        auth: Authenticated user from bearer token
        agent: Injected CX order support agent
        conversation_service: Injected conversation service

    Returns:
        Chat completion response in OpenAI format
    """
    user_id = auth.user_id

    logger.info(
        f"POST /v1/chat/completions - model: {request.model}, messages: {len(request.messages)}, session_id: {request.session_id}, order_id: {request.order_id}, user_id: {user_id}"
    )

    # Extract last user message - fail fast if none present
    user_messages = [msg for msg in request.messages if msg.role == MessageRole.USER]
    user_message = user_messages[-1].content  # IndexError if no user messages

    # Handle session creation or validation
    if request.session_id:
        session_id = request.session_id
        try:
            existing = conversation_service.get_conversation(user_id, session_id)
            if existing:
                logger.info(f"Continuing existing conversation: {session_id}")
            else:
                # Create conversation with provided session_id (e.g., order-based chat)
                conversation_service.create_conversation(session_id, user_id)
                logger.info(
                    f"Created new conversation with provided session_id: {session_id}"
                )
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_id = f"session-{uuid.uuid4().hex}"
        conversation_service.create_conversation(session_id, user_id)
        logger.info(f"Created new conversation: {session_id}")

    # Process message with agent
    response_text = agent.process_message(user_message, session_id, request.order_id)

    # Update conversation metadata
    conversation_service.update_after_message(user_id, session_id, "user", user_message)
    conversation_service.update_after_message(
        user_id, session_id, "assistant", response_text
    )

    prompt_tokens = len(user_message.split())
    completion_tokens = len(response_text.split())

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    response = ChatCompletionResponse.create(
        completion_id=completion_id,
        model=request.model,
        message_content=response_text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        session_id=session_id,
    )

    logger.info(
        f"Response generated: {completion_id}, session: {session_id}, tokens: {response.usage.total_tokens}"
    )

    return response
