"""Conversation repository for DynamoDB access."""

from datetime import UTC, datetime
from typing import Any

from agents.services.models import (
    Conversation,
    ConversationMessage,
    ConversationSummary,
)


class ConversationRepository:
    """Data access layer for conversations table."""

    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        """Initialize repository with DynamoDB client.

        Args:
            dynamodb_client: boto3 DynamoDB client for table operations
            table_name: Name of conversations DynamoDB table
        """
        self._client = dynamodb_client
        self._table_name = table_name

    def create(self, session_id: str, user_id: str) -> ConversationSummary:
        """Create new conversation session.

        Args:
            session_id: Unique session identifier
            user_id: User who owns the conversation

        Returns:
            ConversationSummary for the new conversation
        """
        now = datetime.now(UTC)
        item = {
            "session_id": {"S": session_id},
            "user_id": {"S": user_id},
            "created_at": {"S": now.isoformat()},
            "updated_at": {"S": now.isoformat()},
            "messages": {"L": []},
        }

        self._client.put_item(TableName=self._table_name, Item=item)

        return ConversationSummary(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
            message_count=0,
            preview="",
        )

    def get_by_session_id(self, user_id: str, session_id: str) -> Conversation | None:
        """Retrieve conversation by session ID.

        Args:
            user_id: User who owns the conversation
            session_id: Unique session identifier

        Returns:
            Conversation with full message history, or None if not found
        """
        response = self._client.get_item(
            TableName=self._table_name,
            Key={
                "user_id": {"S": user_id},
                "session_id": {"S": session_id},
            },
        )

        if "Item" not in response:
            return None

        item = response["Item"]
        messages_data = item["messages"]["L"]

        messages = [
            ConversationMessage(
                role=msg["M"]["role"]["S"],
                content=msg["M"]["content"]["S"],
                timestamp=datetime.fromisoformat(msg["M"]["timestamp"]["S"]),
            )
            for msg in messages_data
        ]

        return Conversation(
            session_id=item["session_id"]["S"],
            user_id=item["user_id"]["S"],
            created_at=datetime.fromisoformat(item["created_at"]["S"]),
            updated_at=datetime.fromisoformat(item["updated_at"]["S"]),
            messages=messages,
        )

    def list_by_user_id(self, user_id: str) -> list[ConversationSummary]:
        """List all conversations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of conversation summaries ordered by updated_at descending
        """
        response = self._client.query(
            TableName=self._table_name,
            IndexName="user_id-updated_at-index",
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": {"S": user_id}},
            ScanIndexForward=False,
        )

        summaries = []
        for item in response["Items"]:
            messages_data = item["messages"]["L"]
            message_count = len(messages_data)

            preview = ""
            if messages_data:
                first_msg = messages_data[0]["M"]
                if first_msg["role"]["S"] == "user":
                    preview = first_msg["content"]["S"][:100]

            summaries.append(
                ConversationSummary(
                    session_id=item["session_id"]["S"],
                    user_id=item["user_id"]["S"],
                    created_at=datetime.fromisoformat(item["created_at"]["S"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]["S"]),
                    message_count=message_count,
                    preview=preview,
                )
            )

        return summaries

    def update_metadata(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        timestamp: datetime,
    ) -> None:
        """Update conversation with new message metadata.

        Args:
            user_id: User who owns the conversation
            session_id: Session to update
            role: Message role (user or assistant)
            content: Message content
            timestamp: Message timestamp
        """
        message_item = {
            "M": {
                "role": {"S": role},
                "content": {"S": content},
                "timestamp": {"S": timestamp.isoformat()},
            }
        }

        self._client.update_item(
            TableName=self._table_name,
            Key={
                "user_id": {"S": user_id},
                "session_id": {"S": session_id},
            },
            UpdateExpression="SET messages = list_append(messages, :msg), updated_at = :ts",
            ExpressionAttributeValues={
                ":msg": {"L": [message_item]},
                ":ts": {"S": timestamp.isoformat()},
            },
        )
