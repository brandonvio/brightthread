"""Pydantic models for the CX order support agent.

These models define the structured contracts for LLM outputs and agent state.
They intentionally keep business logic out of the models and use minimal
validation to ensure correctness of structured data.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Intent(StrEnum):
    """Supported top-level intents used for graph routing."""

    ORDER_INQUIRY = "ORDER_INQUIRY"
    ORDER_CHANGE = "ORDER_CHANGE"
    CONFIRMATION = "CONFIRMATION"
    POLICY_CONFIRMATION = "POLICY_CONFIRMATION"
    OFF_TOPIC = "OFF_TOPIC"
    UNCLEAR = "UNCLEAR"


class IntentClassificationOutput(BaseModel):
    """Structured output for intent classification prompts."""

    intent: Intent = Field(..., description="Classified user intent")


class ModificationAction(StrEnum):
    """Supported order modification actions."""

    MODIFY = "modify"
    REMOVE_ITEM = "remove_item"
    UNSUPPORTED = "unsupported"


class PendingModification(BaseModel):
    """Structured representation of a pending order modification."""

    action: ModificationAction = Field(..., description="Modification action type")
    line_item_id: str | None = Field(
        default=None, description="ID of the line item being modified"
    )
    product_name: str = Field(..., description="Product name of the line item")
    size_name: str = Field(..., description="Current size of the line item")
    color_name: str = Field(..., description="Current color of the line item")
    current_quantity: int | None = Field(
        default=None, description="Current quantity of the line item"
    )
    new_quantity: int | None = Field(
        default=None, description="New quantity if changed"
    )
    new_size: str | None = Field(default=None, description="New size name if changed")
    new_color: str | None = Field(default=None, description="New color name if changed")
    reason: str | None = Field(
        default=None, description="Reason when action is unsupported"
    )

    @model_validator(mode="after")
    def _validate_action_requirements(self) -> "PendingModification":
        if self.action == ModificationAction.UNSUPPORTED:
            return self

        if not self.product_name:
            raise ValueError("product_name is required for supported modifications")
        if not self.size_name:
            raise ValueError("size_name is required for supported modifications")
        if not self.color_name:
            raise ValueError("color_name is required for supported modifications")

        if self.action == ModificationAction.MODIFY:
            if (
                self.new_quantity is None
                and self.new_size is None
                and self.new_color is None
            ):
                raise ValueError(
                    "At least one of new_quantity/new_size/new_color is required for modify"
                )
        else:
            # REMOVE_ITEM
            if (
                self.new_quantity is not None
                or self.new_size is not None
                or self.new_color is not None
            ):
                raise ValueError("remove_item must not include new_* fields")

        return self


class PendingModificationStatus(StrEnum):
    """Lifecycle status for a modification derived from user messages."""

    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class ConfirmationInterpretation(StrEnum):
    """Supported confirmation interpretations."""

    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CORRECTION = "CORRECTION"
    UNCLEAR = "UNCLEAR"


class ConfirmationInterpretationOutput(BaseModel):
    """Structured output for confirmation interpretation prompts."""

    interpretation: ConfirmationInterpretation = Field(
        ..., description="Interpretation type"
    )
    corrected_quantity: int | None = Field(
        default=None, description="Corrected quantity when interpretation is CORRECTION"
    )
    corrected_size: str | None = Field(
        default=None, description="Corrected size when interpretation is CORRECTION"
    )
    corrected_color: str | None = Field(
        default=None, description="Corrected color when interpretation is CORRECTION"
    )
    reasoning: str = Field(default="", description="Short reasoning for debugging")


class PolicyConfirmationStatus(StrEnum):
    """Status of user confirmation for policy conditions."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
