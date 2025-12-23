"""Dependency injection configuration for FastAPI."""

import os
from functools import lru_cache
from pathlib import Path

import boto3
from fastapi import Depends
from langchain_aws import ChatBedrock
from langgraph_checkpoint_dynamodb import (
    DynamoDBConfig,
    DynamoDBSaver,
    DynamoDBTableConfig,
)
from sqlalchemy.orm import Session

from agents.cx_order_support_agent import CXOrderSupportAgent
from agents.services.prompt_service import PromptService
from agents.services.conversation_service import ConversationService
from agents.tools.order_tools import OrderTools
from agents.tools.policy_tool import PolicyTool
from db.session import get_db_session
from repositories.artwork_repository import ArtworkRepository
from repositories.company_repository import CompanyRepository
from repositories.conversation_repo import ConversationRepository
from repositories.inventory_repository import InventoryRepository
from repositories.order_line_item_repository import OrderLineItemRepository
from repositories.order_repository import OrderRepository
from repositories.order_status_history_repository import OrderStatusHistoryRepository
from repositories.shipping_address_repository import ShippingAddressRepository
from repositories.user_repository import UserRepository
from services.company_service import CompanyService
from services.order_service import OrderService


# Lazy initialization for DynamoDB-dependent services
# These require AWS credentials and environment variables at runtime
@lru_cache
def _get_dynamodb_client():
    """Lazily create DynamoDB client.

    Uses default boto3 credential chain (env vars, IAM roles, etc.)
    """
    region = os.environ.get("AWS_REGION", "us-west-2")
    return boto3.client("dynamodb", region_name=region)


@lru_cache
def _get_checkpointer() -> DynamoDBSaver:
    """Lazily create DynamoDB checkpointer for LangGraph.

    Note: Uses AWS_PROFILE and AWS_REGION environment variables
    which boto3 picks up automatically through the credential chain.
    """
    table_name = os.environ.get("CHECKPOINTS_TABLE_NAME", "")
    region = os.environ.get("AWS_REGION", "us-west-2")
    config = DynamoDBConfig(
        table_config=DynamoDBTableConfig(
            table_name=table_name,
            ttl_days=30,
        ),
        region_name=region,
    )
    return DynamoDBSaver(config)


@lru_cache
def _get_conversation_repo() -> ConversationRepository:
    """Lazily create conversation repository."""
    table_name = os.environ.get("CONVERSATIONS_TABLE_NAME", "")
    return ConversationRepository(_get_dynamodb_client(), table_name)


@lru_cache
def _get_conversation_service_singleton() -> ConversationService:
    """Lazily create conversation service."""
    return ConversationService(_get_conversation_repo())


def get_order_service(
    session: Session = Depends(get_db_session),
) -> OrderService:
    """Create OrderService with injected database session.

    Args:
        session: SQLAlchemy session for database operations.

    Returns:
        OrderService instance with all required repositories.
    """
    order_repo = OrderRepository(session)
    order_line_item_repo = OrderLineItemRepository(session)
    inventory_repo = InventoryRepository(session)
    status_history_repo = OrderStatusHistoryRepository(session)
    user_repo = UserRepository(session)
    shipping_repo = ShippingAddressRepository(session)
    artwork_repo = ArtworkRepository(session)
    return OrderService(
        order_repo=order_repo,
        order_line_item_repo=order_line_item_repo,
        inventory_repo=inventory_repo,
        status_history_repo=status_history_repo,
        user_repo=user_repo,
        shipping_repo=shipping_repo,
        artwork_repo=artwork_repo,
    )


@lru_cache
def _get_prompt_service() -> PromptService:
    """Lazily create prompt service singleton."""
    prompts_path = Path(__file__).parent / "agents" / "prompts"
    return PromptService(prompts_path)


@lru_cache
def _get_bedrock_model() -> ChatBedrock:
    """Lazily create Bedrock chat model client."""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "")
    region = os.environ.get("BEDROCK_REGION", os.environ.get("AWS_REGION", "us-west-2"))
    return ChatBedrock(model_id=model_id, region_name=region)


def get_cx_agent(
    order_service: OrderService = Depends(get_order_service),
) -> CXOrderSupportAgent:
    """Create CXOrderSupportAgent with injected dependencies.

    Args:
        order_service: Injected order service with database session.

    Returns:
        CXOrderSupportAgent instance ready to process messages.
    """
    prompt_service = _get_prompt_service()
    checkpointer = _get_checkpointer()
    model = _get_bedrock_model()
    order_tools = OrderTools(order_service)
    policy_tool = PolicyTool(model=model, prompt_service=prompt_service)
    return CXOrderSupportAgent(
        prompt_service=prompt_service,
        checkpointer=checkpointer,
        model=model,
        order_tools=order_tools,
        policy_tool=policy_tool,
    )


def get_company_service(
    session: Session = Depends(get_db_session),
) -> CompanyService:
    """Create CompanyService with injected database session."""
    repository = CompanyRepository(session)
    return CompanyService(repository)


def get_conversation_service() -> ConversationService:
    """Provide ConversationService instance."""
    return _get_conversation_service_singleton()
