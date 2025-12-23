"""OpenAI-compatible API models and conversation data models."""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


# =============================================================================
# Conversation History Models
# =============================================================================


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""

    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


class ConversationSummary(BaseModel):
    """Conversation metadata for list views."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User who owns the conversation")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last message timestamp")
    message_count: int = Field(..., description="Total messages in conversation")
    preview: str = Field(..., description="Preview of first user message")


class Conversation(BaseModel):
    """Full conversation with messages."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User who owns the conversation")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last message timestamp")
    messages: list[ConversationMessage] = Field(
        ..., description="Conversation messages in order"
    )


class ConversationListResponse(BaseModel):
    """API response for conversation list."""

    conversations: list[ConversationSummary] = Field(
        ..., description="List of conversation summaries"
    )
    total: int = Field(..., description="Total number of conversations")


# =============================================================================
# OpenAI-Compatible Chat Models
# =============================================================================


class MessageRole(str, Enum):
    """Chat message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A single chat message in OpenAI format."""

    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    model: str = Field(..., description="Model identifier")
    messages: list[ChatMessage] = Field(..., description="Conversation messages")
    temperature: float = Field(
        default=1.0, ge=0, le=2, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=1024, gt=0, description="Maximum tokens to generate"
    )
    stream: bool = Field(default=False, description="Whether to stream responses")
    session_id: str | None = Field(
        default=None, description="Optional session ID for conversation continuation"
    )
    order_id: str = Field(..., description="Order ID for order support context")


class UsageStats(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = Field(..., ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in the completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")


class ChatCompletionChoice(BaseModel):
    """A single completion choice."""

    index: int = Field(..., description="Choice index")
    message: ChatMessage = Field(..., description="Generated message")
    finish_reason: str = Field(..., description="Reason completion finished")


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""

    id: str = Field(..., description="Unique completion identifier")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used for completion")
    choices: list[ChatCompletionChoice] = Field(..., description="Generated choices")
    usage: UsageStats = Field(..., description="Token usage statistics")
    session_id: str = Field(..., description="Session ID for conversation tracking")

    @staticmethod
    def create(
        completion_id: str,
        model: str,
        message_content: str,
        prompt_tokens: int,
        completion_tokens: int,
        session_id: str,
    ) -> "ChatCompletionResponse":
        """Create a chat completion response.

        Args:
            completion_id: Unique identifier for this completion
            model: Model identifier
            message_content: The assistant's message content
            prompt_tokens: Number of tokens in prompt
            completion_tokens: Number of tokens in completion
            session_id: Session ID for conversation tracking

        Returns:
            ChatCompletionResponse instance
        """
        return ChatCompletionResponse(
            id=completion_id,
            created=int(datetime.now(UTC).timestamp()),
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT, content=message_content
                    ),
                    finish_reason="stop",
                )
            ],
            usage=UsageStats(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            session_id=session_id,
        )
