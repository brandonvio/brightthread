"""Unit tests for CXOrderSupportAgent."""

from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agents.cx_order_support_agent import AgentState, CXOrderSupportAgent
from agents.models.cx_order_support import Intent, PendingModificationStatus
from agents.tools.inventory_tool import InventoryTool
from agents.tools.policy_tool import PolicyDecision, PolicyTool


@pytest.fixture
def mock_prompt_service() -> Mock:
    """Create mock PromptService."""
    mock = Mock()
    mock.load_system_prompt.return_value = "Test system prompt"
    return mock


@pytest.fixture
def mock_checkpointer() -> Mock:
    """Create mock checkpointer."""
    return Mock()


@pytest.fixture
def mock_order_tools() -> Mock:
    """Create mock OrderTools."""
    mock = Mock()
    mock.get_order_details.return_value = {"order": {}, "line_items": []}
    mock.modify_line_item.return_value = {"success": True}
    mock.remove_line_item.return_value = {"success": True}
    return mock


@pytest.fixture
def mock_policy_tool() -> Mock:
    """Create mock PolicyTool."""
    mock = Mock(spec=PolicyTool)
    # Default to ALLOWED for most tests
    mock.evaluate_change.return_value = Mock(
        decision=PolicyDecision.ALLOWED,
        change_type="quantity_decrease",
        order_status="CREATED",
        cost_impact=None,
        cost_description=None,
        delivery_impact_days=None,
        delivery_description=None,
        denial_reason=None,
        requires_confirmation=False,
        escalate_to_support=False,
        model_dump=Mock(
            return_value={
                "decision": "allowed",
                "change_type": "quantity_decrease",
                "order_status": "CREATED",
            }
        ),
    )
    return mock


@pytest.fixture
def mock_inventory_tool() -> Mock:
    """Create mock InventoryTool."""
    mock = Mock(spec=InventoryTool)
    # Default to available inventory
    mock.check_availability.return_value = Mock(
        available=True,
        requested_qty=10,
        available_qty=100,
        product_name="Test Product",
        size_name="Medium",
        color_name="Blue",
        alternatives=[],
        model_dump=Mock(
            return_value={
                "available": True,
                "requested_qty": 10,
                "available_qty": 100,
                "alternatives": [],
            }
        ),
    )
    mock.get_alternatives.return_value = []
    return mock


@pytest.fixture
def mock_model() -> Mock:
    """Create mock ChatBedrock model."""
    return Mock()


@pytest.fixture
def agent(
    mock_prompt_service: Mock,
    mock_checkpointer: Mock,
    mock_model: Mock,
    mock_order_tools: Mock,
    mock_policy_tool: Mock,
    mock_inventory_tool: Mock,
) -> CXOrderSupportAgent:
    """Create agent instance with mocked dependencies."""
    return CXOrderSupportAgent(
        prompt_service=mock_prompt_service,
        checkpointer=mock_checkpointer,
        model=mock_model,
        order_tools=mock_order_tools,
        policy_tool=mock_policy_tool,
        inventory_tool=mock_inventory_tool,
    )


def test_intent_classification_order_change(agent: CXOrderSupportAgent) -> None:
    """Test intent classification identifies ORDER_CHANGE intent."""
    agent.model.invoke.return_value = AIMessage(content="ORDER_CHANGE")

    state: AgentState = {
        "messages": [HumanMessage(content="I want to change my order quantity")],
        "response": "",
        "intent": Intent.UNCLEAR,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._intent_classification(state)

    assert result["intent"] == Intent.ORDER_CHANGE


def test_intent_classification_order_inquiry(agent: CXOrderSupportAgent) -> None:
    """Test intent classification identifies ORDER_INQUIRY intent."""
    agent.model.invoke.return_value = AIMessage(content="ORDER_INQUIRY")

    state: AgentState = {
        "messages": [HumanMessage(content="Tell me about this order")],
        "response": "",
        "intent": Intent.UNCLEAR,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._intent_classification(state)

    assert result["intent"] == Intent.ORDER_INQUIRY


def test_intent_classification_off_topic(agent: CXOrderSupportAgent) -> None:
    """Test intent classification identifies OFF_TOPIC intent."""
    agent.model.invoke.return_value = AIMessage(content="OFF_TOPIC")

    state: AgentState = {
        "messages": [HumanMessage(content="What are your product prices?")],
        "response": "",
        "intent": Intent.UNCLEAR,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._intent_classification(state)

    assert result["intent"] == Intent.OFF_TOPIC


def test_intent_classification_invalid_response(agent: CXOrderSupportAgent) -> None:
    """Test intent classification maps invalid model response to UNCLEAR."""
    agent.model.invoke.return_value = AIMessage(content="INVALID_RESPONSE")

    state: AgentState = {
        "messages": [HumanMessage(content="Test message")],
        "response": "",
        "intent": Intent.UNCLEAR,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._intent_classification(state)
    assert result["intent"] == Intent.UNCLEAR


def test_off_topic_response(agent: CXOrderSupportAgent) -> None:
    """Test off-topic response generation."""
    agent.model.invoke.return_value = AIMessage(
        content="I can only help with orders. Please call 888-888-8888."
    )

    state: AgentState = {
        "messages": [HumanMessage(content="What products do you sell?")],
        "response": "",
        "intent": Intent.OFF_TOPIC,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._off_topic_response(state)

    assert result["response"] != ""
    assert isinstance(result["response"], str)


def test_fetch_order_details(agent: CXOrderSupportAgent) -> None:
    """Test fetching order details and generating confirmation."""
    agent.model.invoke.side_effect = [
        AIMessage(
            content=(
                '{"action": "modify", "product_name": "Test Product", "size_name": "Medium", '
                '"color_name": "Blue", "new_quantity": 20, "new_size": null, "new_color": null}'
            )
        ),
        AIMessage(content="You want to change quantity to 20. Is that correct?"),
    ]

    state: AgentState = {
        "messages": [HumanMessage(content="Change quantity to 20")],
        "response": "",
        "intent": Intent.ORDER_CHANGE,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._fetch_order_details(state)

    assert result["order_details"] is not None
    assert result["response"] != ""
    assert isinstance(result["response"], str)
    assert result["pending_modification_id"] is not None
    assert result["pending_modification_status"] == PendingModificationStatus.PENDING


def test_order_summary(agent: CXOrderSupportAgent) -> None:
    """Test order summary generation for inquiry requests."""
    agent.model.invoke.return_value = AIMessage(
        content="Your order is in CREATED status with delivery on Jan 15, 2025."
    )

    state: AgentState = {
        "messages": [HumanMessage(content="Tell me about this order")],
        "response": "",
        "intent": Intent.ORDER_INQUIRY,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._order_summary(state)

    assert result["order_details"] is not None
    assert result["response"] != ""
    assert isinstance(result["response"], str)


def test_confirm_understanding_confirmed(agent: CXOrderSupportAgent) -> None:
    """Test confirmation when LLM interprets user response as CONFIRMED.

    Note: _confirm_understanding no longer executes - it sets state for policy evaluation.
    """
    # Mock the LLM to return CONFIRMED interpretation
    agent.model.invoke.return_value = AIMessage(
        content='{"interpretation": "CONFIRMED", "corrected_quantity": null, "corrected_size": null, "corrected_color": null, "reasoning": "User confirmed"}'
    )

    state: AgentState = {
        "messages": [HumanMessage(content="Yes, that's correct")],
        "response": "",
        "intent": Intent.CONFIRMATION,
        "order_id": "test-order-id",
        "order_details": {"order": {}, "line_items": []},
        "understanding_confirmed": False,
        "pending_modification": {
            "action": "modify",
            "product_name": "Test Product",
            "size_name": "Medium",
            "color_name": "Blue",
            "new_quantity": 25,
            "new_size": None,
            "new_color": None,
        },
        "pending_modification_id": "mod-1",
        "pending_modification_status": PendingModificationStatus.PENDING,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._confirm_understanding(state)

    # Confirmation sets up for policy evaluation - doesn't execute
    assert result["understanding_confirmed"] is True
    assert result["response"] == ""  # Response will be set by policy/execute nodes
    assert result["pending_modification"] is not None  # Still pending for policy check


def test_confirm_understanding_rejected(agent: CXOrderSupportAgent) -> None:
    """Test confirmation when LLM interprets user response as REJECTED."""
    # Mock the LLM to return REJECTED interpretation
    agent.model.invoke.return_value = AIMessage(
        content='{"interpretation": "REJECTED", "corrected_quantity": null, "corrected_size": null, "corrected_color": null, "reasoning": "User rejected"}'
    )

    state: AgentState = {
        "messages": [HumanMessage(content="No, that's not correct")],
        "response": "",
        "intent": Intent.CONFIRMATION,
        "order_id": "test-order-id",
        "order_details": {"order": {}, "line_items": []},
        "understanding_confirmed": False,
        "pending_modification": {
            "action": "modify",
            "product_name": "Test Product",
            "size_name": "Medium",
            "color_name": "Blue",
            "new_quantity": 25,
            "new_size": None,
            "new_color": None,
        },
        "pending_modification_id": "mod-1",
        "pending_modification_status": PendingModificationStatus.PENDING,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._confirm_understanding(state)

    assert result["understanding_confirmed"] is False
    assert "cancelled" in result["response"].lower()
    assert result["pending_modification"] is None
    assert result["pending_modification_status"] == PendingModificationStatus.CANCELLED


def test_confirm_understanding_correction(agent: CXOrderSupportAgent) -> None:
    """Test confirmation when LLM interprets user response as CORRECTION.

    Note: _confirm_understanding no longer executes - it sets state for policy evaluation.
    """
    # Mock the LLM to return CORRECTION interpretation with new color
    agent.model.invoke.return_value = AIMessage(
        content='{"interpretation": "CORRECTION", "corrected_quantity": null, "corrected_size": null, "corrected_color": "White", "reasoning": "User wants white instead"}'
    )

    state: AgentState = {
        "messages": [HumanMessage(content="Actually make it white please")],
        "response": "",
        "intent": Intent.CONFIRMATION,
        "order_id": "test-order-id",
        "order_details": {"order": {}, "line_items": []},
        "understanding_confirmed": False,
        "pending_modification": {
            "action": "modify",
            "product_name": "Test Product",
            "size_name": "Medium",
            "color_name": "Blue",
            "new_quantity": None,
            "new_size": None,
            "new_color": "Red",
        },
        "pending_modification_id": "mod-1",
        "pending_modification_status": PendingModificationStatus.PENDING,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._confirm_understanding(state)

    # Correction is applied, then state is set for policy evaluation
    assert result["understanding_confirmed"] is True
    assert result["response"] == ""  # Response will be set by policy/execute nodes
    # Modification should have the corrected color
    assert result["pending_modification"]["new_color"] == "White"


def test_confirm_understanding_unclear(agent: CXOrderSupportAgent) -> None:
    """Test confirmation when LLM cannot determine user intent."""
    # Mock the LLM to return UNCLEAR interpretation
    agent.model.invoke.return_value = AIMessage(
        content='{"interpretation": "UNCLEAR", "corrected_quantity": null, "corrected_size": null, "corrected_color": null, "reasoning": "User is uncertain"}'
    )

    state: AgentState = {
        "messages": [HumanMessage(content="I'm not sure, let me think")],
        "response": "",
        "intent": Intent.CONFIRMATION,
        "order_id": "test-order-id",
        "order_details": {"order": {}, "line_items": []},
        "understanding_confirmed": False,
        "pending_modification": {
            "action": "modify",
            "product_name": "Test Product",
            "size_name": "Medium",
            "color_name": "Blue",
            "new_quantity": 25,
            "new_size": None,
            "new_color": None,
        },
        "pending_modification_id": "mod-1",
        "pending_modification_status": PendingModificationStatus.PENDING,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    result = agent._confirm_understanding(state)

    assert result["understanding_confirmed"] is False
    assert "clarify" in result["response"].lower()


def test_process_message_with_order_id(
    agent: CXOrderSupportAgent,
) -> None:
    """Test process_message method with order_id parameter."""
    mock_graph_result = {
        "messages": [HumanMessage(content="Test message")],
        "response": "Test response",
        "intent": Intent.ORDER_CHANGE,
        "order_id": "test-order-id",
        "order_details": None,
        "understanding_confirmed": False,
        "pending_modification": None,
        "pending_modification_id": None,
        "pending_modification_status": None,
        "policy_evaluation": None,
        "policy_confirmation_status": None,
        "inventory_check": None,
        "inventory_confirmation_status": None,
    }

    agent.graph.invoke = Mock(return_value=mock_graph_result)
    agent.checkpointer.get = Mock(return_value=None)

    response = agent.process_message(
        message="Test message", session_id="test-session", order_id="test-order-id"
    )

    assert response == "Test response"
    agent.graph.invoke.assert_called_once()
