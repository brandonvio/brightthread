"""LangGraph-based customer support agent using AWS Bedrock."""

import json
import uuid
from decimal import Decimal
from json import JSONDecodeError
from pathlib import Path
from typing import Any, TypedDict

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph
from loguru import logger
from pydantic import ValidationError

from agents.models.cx_order_support import (
    ConfirmationInterpretation,
    ConfirmationInterpretationOutput,
    Intent,
    IntentClassificationOutput,
    ModificationAction,
    PendingModification,
    PendingModificationStatus,
    PolicyConfirmationStatus,
)
from agents.services.prompt_service import PromptService
from agents.tools.order_tools import (
    InvalidColorError,
    InvalidSizeError,
    LineItemNotFoundError,
    OrderTools,
)
from agents.tools.policy_tool import (
    ChangeType,
    PolicyDecision,
    PolicyEvaluationResult,
    PolicyTool,
)


class AgentState(TypedDict):
    """State for the agent conversation."""

    messages: list[Any]  # HumanMessage | SystemMessage
    response: str
    intent: Intent
    order_id: str
    order_details: dict | None
    understanding_confirmed: bool
    pending_modification: dict[str, Any] | None
    pending_modification_id: str | None
    pending_modification_status: PendingModificationStatus | None
    # Policy evaluation state
    policy_evaluation: dict[str, Any] | None
    policy_confirmation_status: PolicyConfirmationStatus | None


class CXOrderSupportAgent:
    """Customer support agent using LangGraph and AWS Bedrock."""

    def __init__(
        self,
        prompt_service: PromptService,
        checkpointer: BaseCheckpointSaver,
        model: ChatBedrock,
        order_tools: OrderTools,
        policy_tool: PolicyTool,
    ) -> None:
        """Initialize agent with prompt service and checkpointer dependencies.

        Args:
            prompt_service: Service for loading system prompts
            checkpointer: DynamoDB checkpointer for conversation state persistence
            model: Bedrock chat model client
            order_tools: Tools wrapper for order operations
            policy_tool: Tool for evaluating order change policies
        """
        self.prompt_service = prompt_service
        self.checkpointer = checkpointer
        self.model = model
        self.order_tools = order_tools
        self.policy_tool = policy_tool
        self.system_prompt = self.prompt_service.load_system_prompt(
            "cx_order_support_agent"
        )

        self.graph = self._build_graph()

        logger.info("CXOrderSupportAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph conversation flow.

        Returns:
            Compiled StateGraph for agent execution with checkpointer
        """
        workflow = StateGraph(AgentState)

        workflow.add_node("intent_classification", self._intent_classification)
        workflow.add_node("unclear_intent_response", self._unclear_intent_response)
        workflow.add_node("off_topic_response", self._off_topic_response)
        workflow.add_node("order_summary", self._order_summary)
        workflow.add_node("fetch_order_details", self._fetch_order_details)
        workflow.add_node("confirm_understanding", self._confirm_understanding)
        workflow.add_node("policy_evaluation", self._policy_evaluation)
        workflow.add_node("policy_condition_response", self._policy_condition_response)
        workflow.add_node(
            "policy_condition_confirmation", self._policy_condition_confirmation
        )
        workflow.add_node("execute_modification", self._execute_modification_node)

        workflow.set_entry_point("intent_classification")

        workflow.add_conditional_edges(
            "intent_classification",
            lambda state: state["intent"],
            {
                Intent.OFF_TOPIC: "off_topic_response",
                Intent.ORDER_INQUIRY: "order_summary",
                Intent.ORDER_CHANGE: "fetch_order_details",
                Intent.CONFIRMATION: "confirm_understanding",
                Intent.POLICY_CONFIRMATION: "policy_condition_confirmation",
                Intent.UNCLEAR: "unclear_intent_response",
            },
        )

        workflow.add_edge("unclear_intent_response", "__end__")
        workflow.add_edge("off_topic_response", "__end__")
        workflow.add_edge("order_summary", "__end__")
        # fetch_order_details generates the confirmation message and ends
        # The user's next message (yes/no) will trigger a new invocation
        # that goes through intent classification again
        workflow.add_edge("fetch_order_details", "__end__")

        # After user confirms understanding, evaluate policy
        workflow.add_conditional_edges(
            "confirm_understanding",
            self._route_after_confirmation,
            {
                "policy_evaluation": "policy_evaluation",
                "end": "__end__",
            },
        )

        # Policy evaluation routes based on decision
        workflow.add_conditional_edges(
            "policy_evaluation",
            self._route_after_policy_evaluation,
            {
                "execute": "execute_modification",
                "conditional": "policy_condition_response",
                "denied": "__end__",
            },
        )

        workflow.add_edge("policy_condition_response", "__end__")

        # When user confirms/rejects policy conditions
        workflow.add_conditional_edges(
            "policy_condition_confirmation",
            self._route_after_policy_condition_confirmation,
            {
                "execute": "execute_modification",
                "cancelled": "__end__",
            },
        )

        workflow.add_edge("execute_modification", "__end__")

        return workflow.compile(checkpointer=self.checkpointer)

    def export_graph_png(self, output_path: str | Path) -> None:
        """Export the compiled LangGraph to a PNG file.

        Args:
            output_path: Destination file path for the PNG (e.g., "agent_graph.png")
        """
        graph = self.graph.get_graph()
        png_bytes: bytes = graph.draw_mermaid_png()
        Path(output_path).write_bytes(png_bytes)

    def _extract_llm_text(self, raw_content: Any) -> str:
        """Extract text from LangChain message content."""
        if isinstance(raw_content, list):
            return "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in raw_content
            ).strip()
        return str(raw_content).strip()

    def _strip_code_fences(self, content: str) -> str:
        """Strip markdown code fences from a response if present."""
        if not content.startswith("```"):
            return content
        lines = content.split("\n")
        return "\n".join(lines[1:-1]).strip()

    def _repair_json_once(
        self, *, schema_name: str, schema: dict[str, Any], bad_output: str
    ) -> str:
        """Ask the model to repair malformed JSON output once."""
        system = (
            f"You are a JSON repair assistant. Produce ONLY valid JSON for schema '{schema_name}'. "
            "Do not include markdown, explanations, or any surrounding text. "
            f"Schema: {json.dumps(schema)}"
        )
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Malformed output:\n{bad_output}"),
        ]
        response = self.model.invoke(messages)
        return self._strip_code_fences(self._extract_llm_text(response.content))

    def _intent_classification(self, state: AgentState) -> AgentState:
        """Classify user message intent.

        If there's a pending policy condition confirmation, routes to that instead.

        Args:
            state: Current agent state with messages

        Returns:
            Updated state with intent classification
        """
        # Check if we're waiting for policy condition confirmation
        policy_status = state.get("policy_confirmation_status")
        if policy_status == PolicyConfirmationStatus.PENDING:
            state["intent"] = Intent.POLICY_CONFIRMATION
            logger.info("Routing to policy condition confirmation (pending)")
            return state

        intent_prompt = self.prompt_service.load_system_prompt(
            "cx_intent_classification"
        )
        messages = [
            SystemMessage(content=intent_prompt),
            *state["messages"],
        ]

        logger.debug("Classifying intent for user message")

        response = self.model.invoke(messages)
        raw = self._extract_llm_text(response.content)
        intent = self._parse_intent(raw)
        state["intent"] = intent
        logger.info(f"Intent classified as: {intent}")

        return state

    def _parse_intent(self, raw: str) -> Intent:
        """Parse intent output from either raw tokens or JSON."""
        content = self._strip_code_fences(raw)
        if content in {i.value for i in Intent}:
            return Intent(content)
        try:
            parsed = IntentClassificationOutput.model_validate_json(content)
            return parsed.intent
        except ValidationError:
            logger.warning(f"Unclear intent classification output: {raw!r}")
            return Intent.UNCLEAR

    def _unclear_intent_response(self, state: AgentState) -> AgentState:
        """Ask the user to clarify when intent classification is unclear."""
        state["response"] = (
            "I can help with your order. Do you want an order summary/status update, "
            "or would you like to change a line item (quantity, size, color, or remove an item)?"
        )
        return state

    def _off_topic_response(self, state: AgentState) -> AgentState:
        """Generate polite decline response for off-topic messages.

        Args:
            state: Current agent state

        Returns:
            Updated state with off-topic response
        """
        off_topic_prompt = self.prompt_service.load_system_prompt(
            "cx_off_topic_response"
        )
        messages = [
            SystemMessage(content=off_topic_prompt),
            *state["messages"],
        ]

        logger.debug("Generating off-topic response")

        response = self.model.invoke(messages)
        state["response"] = response.content

        logger.info("Off-topic response generated")

        return state

    def _order_summary(self, state: AgentState) -> AgentState:
        """Generate order summary for inquiry requests.

        Args:
            state: Current agent state with order_id

        Returns:
            Updated state with order summary response
        """
        logger.debug(f"Generating order summary for order_id={state['order_id']}")

        order_details = self.order_tools.get_order_details(state["order_id"])
        state["order_details"] = order_details

        logger.info(f"Order details fetched for summary, order_id={state['order_id']}")

        summary_prompt = self.prompt_service.load_system_prompt("cx_order_summary")
        user_message = state["messages"][-1].content

        messages = [
            SystemMessage(content=summary_prompt),
            HumanMessage(
                content=f"Order Details: {order_details}\n\nUser Question: {user_message}"
            ),
        ]

        response = self.model.invoke(messages)
        state["response"] = response.content

        logger.info("Order summary generated")

        return state

    def _fetch_order_details(self, state: AgentState) -> AgentState:
        """Fetch order details, parse modification, and generate confirmation message.

        Args:
            state: Current agent state with order_id

        Returns:
            Updated state with order details, parsed modification, and confirmation response
        """
        logger.debug(f"Fetching order details for order_id={state['order_id']}")

        order_details = self.order_tools.get_order_details(state["order_id"])
        state["order_details"] = order_details

        logger.info(
            f"Order details fetched successfully for order_id={state['order_id']}"
        )

        user_message = state["messages"][-1].content

        pending = self._parse_modification(
            order_details=order_details, user_message=user_message
        )
        if pending is None:
            state["pending_modification"] = None
            state["pending_modification_id"] = None
            state["pending_modification_status"] = None
            state["response"] = (
                "I couldn't understand the exact change you want. Please tell me which item "
                "(product name, size, color) and what you want to change (new quantity/size/color), "
                "or say 'remove it'."
            )
            return state

        if pending.action == ModificationAction.UNSUPPORTED:
            state["pending_modification"] = None
            state["pending_modification_id"] = None
            state["pending_modification_status"] = None
            state["response"] = (
                "I understand you'd like to make a change to your order, but I'm only able to help with "
                "modifying quantities, sizes, or colors of line items, or removing items from your order. "
                "For other changes like shipping address or artwork modifications, please contact our "
                "customer service team at 888-888-8888 for assistance."
            )
            return state

        state["pending_modification"] = pending.model_dump()
        state["pending_modification_id"] = uuid.uuid4().hex
        state["pending_modification_status"] = PendingModificationStatus.PENDING

        confirm_prompt = self.prompt_service.load_system_prompt(
            "cx_confirm_understanding"
        )
        messages = [
            SystemMessage(content=confirm_prompt),
            HumanMessage(
                content=f"Order Details: {order_details}\n\nUser Request: {user_message}"
            ),
        ]
        response = self.model.invoke(messages)
        state["response"] = self._extract_llm_text(response.content)

        logger.debug("Confirmation message generated")

        return state

    def _parse_modification(
        self, *, order_details: dict[str, Any], user_message: str
    ) -> PendingModification | None:
        parse_prompt = self.prompt_service.load_system_prompt("cx_parse_modification")
        parse_messages = [
            SystemMessage(content=parse_prompt),
            HumanMessage(
                content=f"Order Details: {order_details}\n\nUser Request: {user_message}"
            ),
        ]
        parse_response = self.model.invoke(parse_messages)
        raw = self._strip_code_fences(self._extract_llm_text(parse_response.content))
        try:
            return self._normalize_and_validate_modification(raw)
        except (JSONDecodeError, ValidationError, ValueError):
            repaired = self._repair_json_once(
                schema_name="PendingModification",
                schema=PendingModification.model_json_schema(),
                bad_output=raw,
            )
            try:
                return self._normalize_and_validate_modification(repaired)
            except (JSONDecodeError, ValidationError, ValueError):
                logger.error(f"Failed to parse/repair modification output: {raw!r}")
                return None

    def _normalize_and_validate_modification(self, content: str) -> PendingModification:
        parsed: dict[str, Any] = json.loads(content)
        action_raw = parsed.get("action", ModificationAction.UNSUPPORTED.value)
        if action_raw in {"modify_quantity", "modify_size", "modify_color"}:
            action_raw = ModificationAction.MODIFY.value

        normalized = {
            "action": action_raw,
            "line_item_id": parsed.get("line_item_id"),
            "product_name": parsed.get("product_name", ""),
            "size_name": parsed.get("size_name") or parsed.get("size", ""),
            "color_name": parsed.get("color_name") or parsed.get("color", ""),
            "current_quantity": parsed.get("current_quantity"),
            "new_quantity": parsed.get("new_quantity"),
            "new_size": parsed.get("new_size"),
            "new_color": parsed.get("new_color"),
            "reason": parsed.get("reason"),
        }
        return PendingModification.model_validate(normalized)

    def _confirm_understanding(self, state: AgentState) -> AgentState:
        """Process user confirmation response. Does NOT execute - routes to policy evaluation.

        Uses LLM to interpret the user's response rather than hardcoded keyword matching.
        When user confirms, sets state for policy evaluation node to check if change is allowed.

        Args:
            state: Current agent state with user response

        Returns:
            Updated state with confirmation status (policy evaluation happens next if confirmed)
        """
        user_message = state["messages"][-1].content

        logger.debug(f"Processing confirmation response: {user_message}")

        pending_status = state.get("pending_modification_status")
        if pending_status == PendingModificationStatus.EXECUTED:
            state["response"] = (
                "That change was already applied. Is there anything else you want to update?"
            )
            return state
        if pending_status == PendingModificationStatus.CANCELLED:
            state["response"] = (
                "That change was cancelled. Is there anything else I can help with on your order?"
            )
            return state

        pending_raw = state.get("pending_modification")
        if pending_raw is None or pending_status != PendingModificationStatus.PENDING:
            state["response"] = (
                "I don't have a pending change to confirm. What would you like to change in your order?"
            )
            return state

        pending_mod = PendingModification.model_validate(pending_raw)

        interpretation = self._interpret_confirmation(user_message, pending_mod)
        logger.info(f"Confirmation interpretation: {interpretation.model_dump()}")

        if interpretation.interpretation == ConfirmationInterpretation.CONFIRMED:
            # User confirmed - mark as confirmed, policy evaluation will happen next
            state["understanding_confirmed"] = True
            # Response will be set by policy_evaluation or execute_modification node
            state["response"] = ""

        elif interpretation.interpretation == ConfirmationInterpretation.CORRECTION:
            # Apply corrections and mark as confirmed for policy evaluation
            corrected = PendingModification.model_validate(
                pending_mod.model_dump()
                | {
                    "new_quantity": (
                        interpretation.corrected_quantity
                        if interpretation.corrected_quantity is not None
                        else pending_mod.new_quantity
                    ),
                    "new_size": interpretation.corrected_size or pending_mod.new_size,
                    "new_color": interpretation.corrected_color
                    or pending_mod.new_color,
                }
            )
            state["pending_modification"] = corrected.model_dump()
            state["understanding_confirmed"] = True
            state["response"] = ""
            logger.info(
                f"Applied corrections to pending modification: {corrected.model_dump()}"
            )

        elif interpretation.interpretation == ConfirmationInterpretation.REJECTED:
            state["understanding_confirmed"] = False
            state["response"] = (
                "No problem, I've cancelled that change. "
                "Is there something else I can help you with regarding your order?"
            )
            state["pending_modification"] = None
            state["pending_modification_status"] = PendingModificationStatus.CANCELLED

        else:  # UNCLEAR
            state["understanding_confirmed"] = False
            state["response"] = (
                "I'm not quite sure what you'd like to do. "
                "Could you please clarify - would you like me to proceed with the change, "
                "or would you prefer something different?"
            )

        return state

    def _route_after_confirmation(self, state: AgentState) -> str:
        """Route after confirm_understanding based on whether user confirmed."""
        if state["understanding_confirmed"]:
            return "policy_evaluation"
        return "end"

    def _interpret_confirmation(
        self, user_message: str, pending_modification: PendingModification
    ) -> ConfirmationInterpretationOutput:
        """Use LLM to interpret the user's confirmation response.

        Args:
            user_message: The user's response to the confirmation question

        Returns:
            Dictionary with interpretation result and any corrected values
        """
        interpret_prompt = self.prompt_service.load_system_prompt(
            "cx_interpret_confirmation"
        )

        messages = [
            SystemMessage(content=interpret_prompt),
            HumanMessage(
                content=(
                    f"Pending change: {pending_modification.model_dump()}\n\n"
                    f"User response: {user_message}"
                )
            ),
        ]

        response = self.model.invoke(messages)
        content = self._strip_code_fences(self._extract_llm_text(response.content))
        try:
            return self._parse_confirmation_interpretation(content)
        except (JSONDecodeError, ValidationError):
            repaired = self._repair_json_once(
                schema_name="ConfirmationInterpretationOutput",
                schema=ConfirmationInterpretationOutput.model_json_schema(),
                bad_output=content,
            )
            try:
                return self._parse_confirmation_interpretation(repaired)
            except (JSONDecodeError, ValidationError):
                logger.error(
                    f"Failed to parse/repair confirmation interpretation: {content!r}"
                )
                return ConfirmationInterpretationOutput(
                    interpretation=ConfirmationInterpretation.UNCLEAR,
                    reasoning="Failed to parse LLM response",
                )

    def _parse_confirmation_interpretation(
        self, content: str
    ) -> ConfirmationInterpretationOutput:
        parsed: dict[str, Any] = json.loads(content)
        interpretation = parsed.get("interpretation") or parsed.get("type")
        normalized = {
            "interpretation": interpretation,
            "corrected_quantity": parsed.get("corrected_quantity"),
            "corrected_size": parsed.get("corrected_size"),
            "corrected_color": parsed.get("corrected_color"),
            "reasoning": parsed.get("reasoning", ""),
        }
        return ConfirmationInterpretationOutput.model_validate(normalized)

    def _execute_modification(
        self, order_id: str, modification: PendingModification
    ) -> str:
        """Execute the parsed modification using OrderTools.

        Supports modifying quantity, size, and/or color in a single request,
        or removing an item from the order.

        Args:
            order_id: The order to modify
            modification: The parsed modification details

        Returns:
            A user-friendly response message
        """
        action = modification.action
        product_name = modification.product_name
        size_name = modification.size_name
        color_name = modification.color_name
        new_quantity = modification.new_quantity
        new_size = modification.new_size
        new_color = modification.new_color

        logger.info(
            f"Executing modification: action={action}, product={product_name}, "
            f"size={size_name}, color={color_name}, new_quantity={new_quantity}, "
            f"new_size={new_size}, new_color={new_color}"
        )

        try:
            if action == ModificationAction.REMOVE_ITEM:
                result = self.order_tools.remove_line_item(
                    order_id=order_id,
                    product_name=product_name,
                    size_name=size_name,
                    color_name=color_name,
                )
                if result.get("success"):
                    return (
                        f"Done! I've removed the {size_name} {color_name} {product_name} "
                        f"from your order. Is there anything else I can help you with?"
                    )
            elif action == ModificationAction.MODIFY:
                # Call modify_line_item with all optional parameters
                # The method handles None values appropriately
                result = self.order_tools.modify_line_item(
                    order_id=order_id,
                    product_name=product_name,
                    size_name=size_name,
                    color_name=color_name,
                    new_quantity=int(new_quantity)
                    if new_quantity is not None
                    else None,
                    new_size_name=str(new_size) if new_size is not None else None,
                    new_color_name=str(new_color) if new_color is not None else None,
                )

                if result.get("success"):
                    return self._build_success_message(
                        product_name,
                        size_name,
                        color_name,
                        new_quantity,
                        new_size,
                        new_color,
                    )
            else:
                return (
                    "I'm sorry, but I can only help with modifying quantities, sizes, or colors "
                    "of line items, or removing items from your order. For other changes, please "
                    "contact our customer service team at 888-888-8888."
                )

            # Handle failure case
            error_msg = result.get("message", "Unknown error")
            logger.warning(f"Modification failed: {error_msg}")
            return (
                f"I wasn't able to complete that change: {error_msg}. "
                f"Please contact our customer service team at 888-888-8888 for assistance."
            )

        except LineItemNotFoundError as e:
            logger.warning(f"Line item not found: {e}")
            return (
                "I couldn't find that item in your order. Could you please verify "
                "the product name, size, and color? You can ask me to show your order "
                "details if you'd like to review what's in your order."
            )
        except InvalidSizeError as e:
            logger.warning(f"Invalid size: {e}")
            return str(e)
        except InvalidColorError as e:
            logger.warning(f"Invalid color: {e}")
            return str(e)

    def _determine_change_type(
        self, modification: PendingModification, order_details: dict[str, Any]
    ) -> ChangeType:
        """Determine the policy change type from a pending modification.

        Args:
            modification: The pending modification with new values
            order_details: Current order details to look up original values

        Returns:
            The appropriate ChangeType for policy evaluation
        """
        if modification.action == ModificationAction.REMOVE_ITEM:
            return ChangeType.REMOVE_ITEM

        # For MODIFY actions, determine the specific change type
        if modification.new_quantity is not None:
            # Find the original quantity from order details
            original_quantity = self._get_original_quantity(modification, order_details)
            if original_quantity is not None:
                if modification.new_quantity > original_quantity:
                    return ChangeType.QUANTITY_INCREASE
                elif modification.new_quantity < original_quantity:
                    return ChangeType.QUANTITY_DECREASE
            # If we can't determine, default to decrease (more restrictive)
            return ChangeType.QUANTITY_DECREASE

        if modification.new_size is not None:
            return ChangeType.SIZE_CHANGE
        if modification.new_color is not None:
            return ChangeType.COLOR_CHANGE

        # Default fallback
        return ChangeType.QUANTITY_DECREASE

    def _get_original_quantity(
        self, modification: PendingModification, order_details: dict[str, Any]
    ) -> int | None:
        """Look up the original quantity for a line item from order details.

        Args:
            modification: The pending modification identifying the line item
            order_details: Current order details with line items

        Returns:
            Original quantity if found, None otherwise
        """
        line_items = order_details.get("line_items", [])
        for item in line_items:
            if (
                item.get("product_name", "").lower()
                == modification.product_name.lower()
                and item.get("size", "").lower() == modification.size_name.lower()
                and item.get("color", "").lower() == modification.color_name.lower()
            ):
                return item.get("quantity")
        return None

    def _policy_evaluation(self, state: AgentState) -> AgentState:
        """Evaluate the pending modification against change policies.

        Called after user confirms understanding. Checks if the change is:
        - ALLOWED: proceeds to execution
        - CONDITIONAL: asks user to confirm conditions (cost/delay)
        - DENIED: informs user and ends

        Args:
            state: Current agent state with confirmed pending modification

        Returns:
            Updated state with policy evaluation result
        """
        pending_raw = state.get("pending_modification")
        if pending_raw is None:
            state["response"] = (
                "I don't have a pending change to evaluate. "
                "What would you like to change in your order?"
            )
            state["policy_evaluation"] = None
            return state

        pending_mod = PendingModification.model_validate(pending_raw)
        order_details = state.get("order_details", {})
        order_status = order_details.get("status", "CREATED")

        # Determine the change type from the modification (needs order_details to compare quantities)
        change_type = self._determine_change_type(pending_mod, order_details)

        # Get order total for refund calculations
        order_total = Decimal(str(order_details.get("total_amount", "0")))

        # Find the affected line item amount for percentage-based cost calculations
        affected_amount = Decimal("0")
        line_items = order_details.get("line_items", [])
        for item in line_items:
            if (
                item.get("product_name", "").lower() == pending_mod.product_name.lower()
                and item.get("size", "").lower() == pending_mod.size_name.lower()
                and item.get("color", "").lower() == pending_mod.color_name.lower()
            ):
                # Calculate line item total: quantity * unit_price
                quantity = item.get("quantity", 0)
                unit_price = Decimal(str(item.get("unit_price", "0")))
                affected_amount = quantity * unit_price
                break

        # Evaluate against policy
        evaluation = self.policy_tool.evaluate_change(
            order_status=order_status,
            change_type=change_type,
            affected_amount=affected_amount,
            order_total=order_total,
        )

        state["policy_evaluation"] = evaluation.model_dump(mode="json")

        logger.info(
            f"Policy evaluation: status={order_status}, change={change_type.value}, "
            f"decision={evaluation.decision.value}"
        )

        # Set response based on decision
        if evaluation.decision == PolicyDecision.DENIED:
            state["response"] = self._build_denial_response(
                evaluation=evaluation,
                order_details=order_details,
                pending_modification=pending_raw,
            )
            state["pending_modification"] = None
            state["pending_modification_status"] = PendingModificationStatus.CANCELLED

        elif evaluation.decision == PolicyDecision.CONDITIONAL:
            # Response will be set by policy_condition_response node
            state["policy_confirmation_status"] = PolicyConfirmationStatus.PENDING
            state["response"] = ""

        # ALLOWED: response will be set by execute_modification node
        return state

    def _route_after_policy_evaluation(self, state: AgentState) -> str:
        """Route after policy evaluation based on decision."""
        policy_eval = state.get("policy_evaluation")
        if policy_eval is None:
            return "end"

        decision = policy_eval.get("decision")
        if decision == PolicyDecision.ALLOWED.value:
            return "execute"
        elif decision == PolicyDecision.CONDITIONAL.value:
            return "conditional"
        else:
            return "denied"

    def _build_denial_response(
        self,
        evaluation: PolicyEvaluationResult,
        order_details: dict[str, Any],
        pending_modification: dict[str, Any] | None,
    ) -> str:
        """Generate natural response for denied changes using LLM.

        Args:
            evaluation: Policy evaluation result with denial reason
            order_details: Current order information
            pending_modification: What the customer wanted to change

        Returns:
            Natural conversational response explaining the denial
        """
        denial_prompt = self.prompt_service.load_system_prompt("cx_policy_denial")

        context = {
            "order_details": order_details,
            "pending_modification": pending_modification,
            "policy_evaluation": evaluation.model_dump(mode="json"),
        }

        messages = [
            SystemMessage(content=denial_prompt),
            HumanMessage(
                content=f"Context:\n{json.dumps(context, indent=2, default=str)}"
            ),
        ]

        response = self.model.invoke(messages)
        return self._extract_llm_text(response.content)

    def _policy_condition_response(self, state: AgentState) -> AgentState:
        """Generate natural response informing user of policy conditions.

        Uses LLM to craft a conversational response explaining the conditions
        rather than a mechanical templated message.

        Args:
            state: Current agent state with conditional policy evaluation

        Returns:
            Updated state with natural condition explanation and confirmation request
        """
        policy_eval = state.get("policy_evaluation")
        if policy_eval is None:
            state["response"] = "Something went wrong. Please try again."
            return state

        pending_raw = state.get("pending_modification")
        order_details = state.get("order_details", {})

        # Load the policy response prompt and let LLM craft a natural response
        policy_response_prompt = self.prompt_service.load_system_prompt(
            "cx_policy_response"
        )

        context = {
            "order_details": order_details,
            "pending_modification": pending_raw,
            "policy_evaluation": policy_eval,
        }

        messages = [
            SystemMessage(content=policy_response_prompt),
            HumanMessage(
                content=f"Context:\n{json.dumps(context, indent=2, default=str)}"
            ),
        ]

        response = self.model.invoke(messages)
        state["response"] = self._extract_llm_text(response.content)

        logger.debug("Generated natural policy condition response via LLM")

        return state

    def _policy_condition_confirmation(self, state: AgentState) -> AgentState:
        """Process user response to policy conditions (accept/reject).

        Args:
            state: Current agent state with user's response to conditions

        Returns:
            Updated state with confirmation status
        """
        user_message = state["messages"][-1].content

        logger.debug(f"Processing policy condition confirmation: {user_message}")

        # Use simple confirmation interpretation for policy conditions
        pending_raw = state.get("pending_modification")
        if pending_raw is None:
            state["response"] = (
                "I don't have a pending change. What would you like to do?"
            )
            state["policy_confirmation_status"] = None
            return state

        pending_mod = PendingModification.model_validate(pending_raw)
        interpretation = self._interpret_confirmation(user_message, pending_mod)

        if interpretation.interpretation == ConfirmationInterpretation.CONFIRMED:
            state["policy_confirmation_status"] = PolicyConfirmationStatus.ACCEPTED
            # Response will be set by execute_modification node
            state["response"] = ""

        elif interpretation.interpretation == ConfirmationInterpretation.REJECTED:
            state["policy_confirmation_status"] = PolicyConfirmationStatus.REJECTED
            state["response"] = (
                "No problem, I've cancelled that change. "
                "Is there something else I can help you with regarding your order?"
            )
            state["pending_modification"] = None
            state["pending_modification_status"] = PendingModificationStatus.CANCELLED

        else:  # UNCLEAR or CORRECTION
            state["response"] = (
                "I need a clear yes or no. Would you like me to proceed with the change "
                "given the conditions I mentioned?"
            )

        return state

    def _route_after_policy_condition_confirmation(self, state: AgentState) -> str:
        """Route after policy condition confirmation."""
        policy_status = state.get("policy_confirmation_status")
        if policy_status == PolicyConfirmationStatus.ACCEPTED.value:
            return "execute"
        return "cancelled"

    def _execute_modification_node(self, state: AgentState) -> AgentState:
        """Execute the modification and set response. Node wrapper for _execute_modification.

        Args:
            state: Current agent state with confirmed modification

        Returns:
            Updated state with execution result
        """
        pending_raw = state.get("pending_modification")
        if pending_raw is None:
            state["response"] = "No pending modification to execute."
            return state

        pending_mod = PendingModification.model_validate(pending_raw)
        result = self._execute_modification(state["order_id"], pending_mod)

        state["response"] = result
        state["pending_modification"] = None
        state["pending_modification_status"] = PendingModificationStatus.EXECUTED

        return state

    def _build_success_message(
        self,
        product_name: str,
        size_name: str,
        color_name: str,
        new_quantity: int | None,
        new_size: str | None,
        new_color: str | None,
    ) -> str:
        """Build a user-friendly success message describing all changes made.

        Args:
            product_name: The product that was modified
            size_name: The original size
            color_name: The original color
            new_quantity: New quantity if changed, else None
            new_size: New size if changed, else None
            new_color: New color if changed, else None

        Returns:
            A formatted success message describing the changes
        """
        changes = []

        if new_quantity is not None:
            changes.append(f"quantity to {new_quantity}")
        if new_size is not None:
            changes.append(f"size from {size_name} to {new_size}")
        if new_color is not None:
            changes.append(f"color from {color_name} to {new_color}")

        if len(changes) == 1:
            change_desc = changes[0]
        elif len(changes) == 2:
            change_desc = f"{changes[0]} and {changes[1]}"
        else:
            change_desc = f"{changes[0]}, {changes[1]}, and {changes[2]}"

        return (
            f"Done! I've updated the {product_name}: {change_desc}. "
            f"Is there anything else I can help you with?"
        )

    def process_message(self, message: str, session_id: str, order_id: str) -> str:
        """Process a user message and return agent response.

        Args:
            message: User's message text
            session_id: Session identifier for conversation state
            order_id: Order ID for the conversation context

        Returns:
            Agent's response text
        """
        logger.info(
            f"Processing message for session {session_id}, order {order_id}: {message[:100]}"
        )

        config = {"configurable": {"thread_id": session_id}}

        # Try to get previous state from checkpointer to preserve pending_modification
        previous_pending_modification = None
        previous_order_details = None
        previous_modification_id = None
        previous_modification_status = None
        previous_policy_evaluation = None
        previous_policy_confirmation_status = None
        checkpoint = self.checkpointer.get(config)
        if checkpoint and "channel_values" in checkpoint:
            channel_values = checkpoint["channel_values"]
            previous_pending_modification = channel_values.get("pending_modification")
            previous_order_details = channel_values.get("order_details")
            previous_modification_id = channel_values.get("pending_modification_id")
            previous_modification_status = channel_values.get(
                "pending_modification_status"
            )
            previous_policy_evaluation = channel_values.get("policy_evaluation")
            previous_policy_confirmation_status = channel_values.get(
                "policy_confirmation_status"
            )
            logger.debug(
                "Retrieved previous state: "
                f"pending_modification_id={previous_modification_id}, "
                f"pending_modification_status={previous_modification_status}, "
                f"policy_confirmation_status={previous_policy_confirmation_status}"
            )

        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "response": "",
            "intent": Intent.UNCLEAR,
            "order_id": order_id,
            "order_details": previous_order_details,
            "understanding_confirmed": False,
            "pending_modification": previous_pending_modification,
            "pending_modification_id": previous_modification_id,
            "pending_modification_status": previous_modification_status,
            "policy_evaluation": previous_policy_evaluation,
            "policy_confirmation_status": previous_policy_confirmation_status,
        }

        result = self.graph.invoke(initial_state, config)
        response = result["response"]

        logger.info(f"Generated response: {response[:100]}")
        return response
