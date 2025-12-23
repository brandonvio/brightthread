"""Policy tool for evaluating order modification requests against change policies."""

import json
from decimal import Decimal
from enum import StrEnum
from pathlib import Path

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from agents.services.prompt_service import PromptService


class ChangeType(StrEnum):
    """Types of changes that can be requested on an order."""

    QUANTITY_INCREASE = "quantity_increase"
    QUANTITY_DECREASE = "quantity_decrease"
    SIZE_CHANGE = "size_change"
    COLOR_CHANGE = "color_change"
    ARTWORK_CHANGE = "artwork_change"
    ADDRESS_CHANGE = "address_change"
    CANCELLATION = "cancellation"
    REMOVE_ITEM = "remove_item"


class PolicyDecision(StrEnum):
    """Result of policy evaluation."""

    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    DENIED = "denied"


class PolicyEvaluationResult(BaseModel):
    """Result of evaluating a change request against policies."""

    decision: PolicyDecision = Field(..., description="Whether the change is allowed")
    change_type: str = Field(..., description="The type of change requested")
    order_status: str = Field(..., description="Current order status")
    cost_impact: Decimal | None = Field(
        default=None, description="Additional cost if conditional"
    )
    cost_description: str | None = Field(
        default=None, description="Description of cost impact"
    )
    delivery_impact_days: int | None = Field(
        default=None, description="Additional days added to delivery"
    )
    delivery_description: str | None = Field(
        default=None, description="Description of delivery impact"
    )
    denial_reason: str | None = Field(
        default=None, description="Reason for denial if denied"
    )
    requires_confirmation: bool = Field(
        default=False, description="Whether user confirmation is required"
    )
    escalate_to_support: bool = Field(
        default=False, description="Whether to escalate to human support"
    )


class PolicyTool:
    """Tool for evaluating order modification requests against change policies.

    Loads policies from change-policies.md and uses an LLM to evaluate whether
    requested changes are allowed, conditional, or denied based on order status.
    """

    def __init__(
        self,
        model: ChatBedrock,
        prompt_service: PromptService,
        policies_dir: Path | None = None,
    ) -> None:
        """Initialize policy tool.

        Args:
            model: Bedrock chat model for policy evaluation
            prompt_service: Service for loading prompt templates
            policies_dir: Path to directory containing policy documents.
                         If None, uses default relative to this file.
        """
        self.model = model
        self.prompt_service = prompt_service
        if policies_dir is None:
            policies_dir = Path(__file__).parent.parent / "policies"
        self.policies_dir = policies_dir
        self._policy_document: str | None = None

    def load_policy_document(self) -> str:
        """Load the change policies markdown document.

        Returns:
            Contents of change-policies.md

        Raises:
            FileNotFoundError: If policy document not found
        """
        if self._policy_document is not None:
            return self._policy_document

        policy_path = self.policies_dir / "change-policies.md"
        logger.debug(f"Loading policy document from {policy_path}")

        with open(policy_path, "r", encoding="utf-8") as f:
            self._policy_document = f.read()

        logger.info("Policy document loaded successfully")
        return self._policy_document

    def _extract_llm_text(self, raw_content) -> str:
        """Extract text from LangChain message content."""
        if isinstance(raw_content, list):
            return "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in raw_content
            ).strip()
        return str(raw_content).strip()

    def _extract_json(self, content: str) -> str:
        """Extract JSON from response, handling code fences and extra text.

        The LLM may return JSON wrapped in code fences with extra commentary after.
        This method extracts just the JSON portion.
        """
        # If content starts with code fence, extract content between fences
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.index("```", start)
            return content[start:end].strip()
        elif content.startswith("```"):
            # Generic code fence
            lines = content.split("\n")
            # Find the closing fence
            end_idx = len(lines) - 1
            for i in range(1, len(lines)):
                if lines[i].startswith("```"):
                    end_idx = i
                    break
            return "\n".join(lines[1:end_idx]).strip()

        # Try to find JSON object directly
        if "{" in content:
            start = content.index("{")
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(content[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return content[start:i + 1]

        return content.strip()

    def evaluate_change(
        self,
        order_status: str,
        change_type: ChangeType | str,
        affected_amount: Decimal | None = None,
        order_total: Decimal | None = None,
    ) -> PolicyEvaluationResult:
        """Evaluate whether a change is allowed based on policy document.

        Uses the LLM to read the policy document and determine the appropriate
        response for the given order status and change type.

        Args:
            order_status: Current status of the order (CREATED, APPROVED, etc.)
            change_type: Type of change being requested
            affected_amount: Amount of affected line items (for percentage calculations)
            order_total: Total order amount (for refund calculations)

        Returns:
            PolicyEvaluationResult with decision and any conditions
        """
        status_upper = order_status.upper()
        change_type_str = (
            change_type.value if isinstance(change_type, ChangeType) else str(change_type)
        )

        # Load the policy document and prompt template
        policy_document = self.load_policy_document()
        prompt_template = self.prompt_service.load_system_prompt("cx_policy_evaluation")

        # Build the evaluation prompt by substituting placeholders
        prompt = prompt_template.format(
            policy_document=policy_document,
            order_status=status_upper,
            change_type=change_type_str,
            affected_amount=f"{affected_amount:.2f}" if affected_amount else "0.00",
            order_total=f"{order_total:.2f}" if order_total else "0.00",
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(
                content=f"Evaluate the {change_type_str} request for an order in {status_upper} status."
            ),
        ]

        logger.debug(f"Evaluating policy: status={status_upper}, change_type={change_type_str}")

        response = self.model.invoke(messages)
        raw = self._extract_llm_text(response.content)
        content = self._extract_json(raw)

        try:
            parsed = json.loads(content)
            result = PolicyEvaluationResult.model_validate(parsed)
            logger.info(
                f"Policy evaluation: status={status_upper}, change={change_type_str}, "
                f"decision={result.decision.value}"
            )
            return result
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(
                f"Failed to parse policy evaluation response: {raw!r}, error: {e}"
            )
            # Fail safe - deny and escalate
            return PolicyEvaluationResult(
                decision=PolicyDecision.DENIED,
                change_type=change_type_str,
                order_status=status_upper,
                denial_reason="Unable to evaluate policy - please contact support",
                escalate_to_support=True,
            )

    def get_policy_summary(self, order_status: str) -> str:
        """Get a human-readable summary of what changes are allowed for an order status.

        Args:
            order_status: Current status of the order

        Returns:
            Summary string of allowed/conditional/denied changes
        """
        # Load policy document and return relevant section
        policy_document = self.load_policy_document()
        status_upper = order_status.upper()

        # Find the section for this status
        marker = f"### {status_upper} State"
        if marker in policy_document:
            start = policy_document.index(marker)
            # Find the next section or end
            next_section = policy_document.find("\n### ", start + 1)
            if next_section == -1:
                next_section = policy_document.find("\n## ", start + 1)
            if next_section == -1:
                section = policy_document[start:]
            else:
                section = policy_document[start:next_section]
            return section.strip()

        return f"No policy information found for {status_upper} orders."
