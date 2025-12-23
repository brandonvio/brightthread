"""Inventory tools for agent to check availability and find alternatives."""

import uuid

from pydantic import BaseModel

from services.inventory_service import InventoryService


class InventoryAlternative(BaseModel):
    """An alternative inventory option with available stock."""

    product_name: str
    size_name: str
    color_name: str
    available_qty: int
    inventory_id: str


class InventoryCheckResult(BaseModel):
    """Result of an inventory availability check."""

    available: bool
    requested_qty: int
    available_qty: int
    product_name: str
    size_name: str
    color_name: str
    alternatives: list[InventoryAlternative]


class InventoryTool:
    """Tools for inventory-related operations."""

    def __init__(self, inventory_service: InventoryService) -> None:
        """Initialize inventory tool with InventoryService dependency.

        Args:
            inventory_service: Service for inventory operations
        """
        self._inventory_service = inventory_service

    def check_availability(
        self,
        product_id: uuid.UUID,
        color_id: uuid.UUID,
        size_id: uuid.UUID,
        quantity: int,
        product_name: str,
        size_name: str,
        color_name: str,
    ) -> InventoryCheckResult:
        """Check if requested quantity is available for a specific product/size/color.

        Args:
            product_id: UUID of the product
            color_id: UUID of the color
            size_id: UUID of the size
            quantity: Requested quantity
            product_name: Human-readable product name
            size_name: Human-readable size name
            color_name: Human-readable color name

        Returns:
            InventoryCheckResult with availability status and alternatives if insufficient
        """
        availability = self._inventory_service.check_availability(
            product_id=product_id,
            color_id=color_id,
            size_id=size_id,
            quantity=quantity,
        )

        alternatives: list[InventoryAlternative] = []

        # If insufficient, find alternatives
        if not availability.available:
            alternatives = self.get_alternatives(
                product_id=product_id,
                min_quantity=quantity,
                exclude_color_id=color_id,
                exclude_size_id=size_id,
            )

        return InventoryCheckResult(
            available=availability.available,
            requested_qty=quantity,
            available_qty=availability.available_qty,
            product_name=product_name,
            size_name=size_name,
            color_name=color_name,
            alternatives=alternatives,
        )

    def get_alternatives(
        self,
        product_id: uuid.UUID,
        min_quantity: int,
        exclude_color_id: uuid.UUID | None = None,
        exclude_size_id: uuid.UUID | None = None,
    ) -> list[InventoryAlternative]:
        """Find alternative inventory options for the same product with sufficient stock.

        Args:
            product_id: UUID of the product
            min_quantity: Minimum quantity required
            exclude_color_id: Optional color ID to exclude (current selection)
            exclude_size_id: Optional size ID to exclude (current selection)

        Returns:
            List of alternatives with sufficient inventory, sorted by available_qty desc
        """
        # Get all inventory for this product
        inventory_items = self._inventory_service.get_inventory_by_product(product_id)

        alternatives: list[InventoryAlternative] = []

        for item in inventory_items:
            # Skip the current selection if both match
            if item.color_id == exclude_color_id and item.size_id == exclude_size_id:
                continue

            # Only include items with sufficient stock
            if item.available_qty >= min_quantity:
                # Get enriched data for names
                enriched = self._inventory_service.get_enriched_inventory_by_id(item.id)
                alternatives.append(
                    InventoryAlternative(
                        product_name=enriched.product_name,
                        size_name=enriched.size_name,
                        color_name=enriched.color_name,
                        available_qty=enriched.available_qty,
                        inventory_id=str(item.id),
                    )
                )

        # Sort by available quantity descending
        alternatives.sort(key=lambda x: x.available_qty, reverse=True)

        # Limit to top 5 alternatives
        return alternatives[:5]

    def get_partial_availability(
        self,
        product_id: uuid.UUID,
        color_id: uuid.UUID,
        size_id: uuid.UUID,
        product_name: str,
        size_name: str,
        color_name: str,
    ) -> InventoryAlternative | None:
        """Get current availability as a partial fulfillment option.

        Args:
            product_id: UUID of the product
            color_id: UUID of the color
            size_id: UUID of the size
            product_name: Human-readable product name
            size_name: Human-readable size name
            color_name: Human-readable color name

        Returns:
            InventoryAlternative with current stock, or None if no stock
        """
        availability = self._inventory_service.check_availability(
            product_id=product_id,
            color_id=color_id,
            size_id=size_id,
            quantity=1,  # Check if any available
        )

        if availability.available_qty > 0:
            # Get the inventory ID
            inventory_items = self._inventory_service.get_inventory_by_product(
                product_id
            )
            for item in inventory_items:
                if item.color_id == color_id and item.size_id == size_id:
                    return InventoryAlternative(
                        product_name=product_name,
                        size_name=size_name,
                        color_name=color_name,
                        available_qty=availability.available_qty,
                        inventory_id=str(item.id),
                    )

        return None
