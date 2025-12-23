"""Order tools for agent to fetch and modify order details."""

import uuid

from services.order_service import (
    InsufficientInventoryError,
    InvalidOrderModificationError,
    OrderService,
    OrderValidationError,
)


class LineItemNotFoundError(Exception):
    """Raised when a line item cannot be found by the given criteria."""

    pass


class InvalidSizeError(Exception):
    """Raised when a requested size is not available for the product."""

    pass


class InvalidColorError(Exception):
    """Raised when a requested color is not available for the product."""

    pass


class OrderTools:
    """Tools for order-related operations."""

    def __init__(self, order_service: OrderService) -> None:
        """Initialize order tools with OrderService dependency.

        Args:
            order_service: Service for order operations
        """
        self._order_service = order_service

    def get_order_details(self, order_id: str) -> dict:
        """Fetch order details including line items.

        Args:
            order_id: String UUID of the order

        Returns:
            Dictionary with order details as JSON-serializable dict
        """
        order_uuid = uuid.UUID(order_id)
        order = self._order_service.get_enriched_order(order_uuid)

        # Pydantic model - convert to dict with JSON-safe serialization
        return order.model_dump(mode="json")

    def modify_line_item(
        self,
        order_id: str,
        line_item_id: str | None = None,
        product_name: str | None = None,
        size_name: str | None = None,
        color_name: str | None = None,
        new_quantity: int | None = None,
        new_size_name: str | None = None,
        new_color_name: str | None = None,
    ) -> dict:
        """Modify a line item's quantity, size, or color.

        The line item can be identified either by line_item_id directly,
        or by product_name + size_name + color_name combination.

        Args:
            order_id: String UUID of the order
            line_item_id: Optional string UUID of the line item
            product_name: Optional product name to identify line item
            size_name: Optional size name to identify line item
            color_name: Optional color name to identify line item
            new_quantity: New quantity (if changing)
            new_size_name: New size name (if changing)
            new_color_name: New color name (if changing)

        Returns:
            Dictionary with result status and updated order details

        Raises:
            LineItemNotFoundError: If line item cannot be found
            InvalidSizeError: If new size is not available
            InvalidColorError: If new color is not available
        """
        order_uuid = uuid.UUID(order_id)
        order = self._order_service.get_enriched_order(order_uuid)

        # Find the line item
        target_line_item = None
        if line_item_id:
            line_item_uuid = uuid.UUID(line_item_id)
            for item in order.line_items:
                if item.id == line_item_uuid:
                    target_line_item = item
                    break
        elif product_name and size_name and color_name:
            for item in order.line_items:
                if (
                    item.product_name.lower() == product_name.lower()
                    and item.size.lower() == size_name.lower()
                    and item.color.lower() == color_name.lower()
                ):
                    target_line_item = item
                    break

        if not target_line_item:
            raise LineItemNotFoundError(
                f"Could not find line item matching criteria. "
                f"line_item_id={line_item_id}, product={product_name}, "
                f"size={size_name}, color={color_name}"
            )

        # Resolve new size/color to IDs if provided
        new_size_id = None
        new_color_id = None

        # Get product_id from the inventory
        inventory = self._order_service._inventory_repo.get_by_id(
            target_line_item.inventory_id
        )
        product_id = inventory.product_id

        if new_size_name:
            available_sizes = self._order_service.get_available_sizes_for_product(
                product_id
            )
            matching_size = None
            for size in available_sizes:
                if size["name"].lower() == new_size_name.lower():
                    matching_size = size
                    break

            if not matching_size:
                size_names = [s["name"] for s in available_sizes]
                raise InvalidSizeError(
                    f"Size '{new_size_name}' is not available for this product. "
                    f"Available sizes: {', '.join(size_names)}"
                )
            new_size_id = uuid.UUID(matching_size["id"])

        if new_color_name:
            available_colors = self._order_service.get_available_colors_for_product(
                product_id
            )
            matching_color = None
            for color in available_colors:
                if color["name"].lower() == new_color_name.lower():
                    matching_color = color
                    break

            if not matching_color:
                color_names = [c["name"] for c in available_colors]
                raise InvalidColorError(
                    f"Color '{new_color_name}' is not available for this product. "
                    f"Available colors: {', '.join(color_names)}"
                )
            new_color_id = uuid.UUID(matching_color["id"])

        try:
            updated_order = self._order_service.modify_line_item(
                order_id=order_uuid,
                line_item_id=target_line_item.id,
                new_quantity=new_quantity,
                new_size_id=new_size_id,
                new_color_id=new_color_id,
            )
            return {
                "success": True,
                "message": "Line item modified successfully",
                "order": updated_order.model_dump(mode="json"),
            }
        except InsufficientInventoryError as e:
            return {
                "success": False,
                "error": "insufficient_inventory",
                "message": str(e),
            }
        except InvalidOrderModificationError as e:
            return {
                "success": False,
                "error": "modification_not_allowed",
                "message": str(e),
            }

    def remove_line_item(
        self,
        order_id: str,
        line_item_id: str | None = None,
        product_name: str | None = None,
        size_name: str | None = None,
        color_name: str | None = None,
    ) -> dict:
        """Remove a line item from an order.

        The line item can be identified either by line_item_id directly,
        or by product_name + size_name + color_name combination.

        Args:
            order_id: String UUID of the order
            line_item_id: Optional string UUID of the line item
            product_name: Optional product name to identify line item
            size_name: Optional size name to identify line item
            color_name: Optional color name to identify line item

        Returns:
            Dictionary with result status and updated order details

        Raises:
            LineItemNotFoundError: If line item cannot be found
        """
        order_uuid = uuid.UUID(order_id)
        order = self._order_service.get_enriched_order(order_uuid)

        # Find the line item
        target_line_item = None
        if line_item_id:
            line_item_uuid = uuid.UUID(line_item_id)
            for item in order.line_items:
                if item.id == line_item_uuid:
                    target_line_item = item
                    break
        elif product_name and size_name and color_name:
            for item in order.line_items:
                if (
                    item.product_name.lower() == product_name.lower()
                    and item.size.lower() == size_name.lower()
                    and item.color.lower() == color_name.lower()
                ):
                    target_line_item = item
                    break

        if not target_line_item:
            raise LineItemNotFoundError(
                f"Could not find line item matching criteria. "
                f"line_item_id={line_item_id}, product={product_name}, "
                f"size={size_name}, color={color_name}"
            )

        try:
            updated_order = self._order_service.remove_line_item(
                order_id=order_uuid,
                line_item_id=target_line_item.id,
            )
            return {
                "success": True,
                "message": "Line item removed successfully",
                "order": updated_order.model_dump(mode="json"),
            }
        except InvalidOrderModificationError as e:
            return {
                "success": False,
                "error": "modification_not_allowed",
                "message": str(e),
            }
        except OrderValidationError as e:
            return {
                "success": False,
                "error": "validation_error",
                "message": str(e),
            }

    def get_available_options_for_line_item(
        self,
        order_id: str,
        line_item_id: str | None = None,
        product_name: str | None = None,
        size_name: str | None = None,
        color_name: str | None = None,
    ) -> dict:
        """Get available sizes and colors for a line item's product.

        The line item can be identified either by line_item_id directly,
        or by product_name + size_name + color_name combination.

        Args:
            order_id: String UUID of the order
            line_item_id: Optional string UUID of the line item
            product_name: Optional product name to identify line item
            size_name: Optional size name to identify line item
            color_name: Optional color name to identify line item

        Returns:
            Dictionary with available sizes and colors for the product

        Raises:
            LineItemNotFoundError: If line item cannot be found
        """
        order_uuid = uuid.UUID(order_id)
        order = self._order_service.get_enriched_order(order_uuid)

        # Find the line item
        target_line_item = None
        if line_item_id:
            line_item_uuid = uuid.UUID(line_item_id)
            for item in order.line_items:
                if item.id == line_item_uuid:
                    target_line_item = item
                    break
        elif product_name and size_name and color_name:
            for item in order.line_items:
                if (
                    item.product_name.lower() == product_name.lower()
                    and item.size.lower() == size_name.lower()
                    and item.color.lower() == color_name.lower()
                ):
                    target_line_item = item
                    break

        if not target_line_item:
            raise LineItemNotFoundError(
                f"Could not find line item matching criteria. "
                f"line_item_id={line_item_id}, product={product_name}, "
                f"size={size_name}, color={color_name}"
            )

        # Get product_id from the inventory
        inventory = self._order_service._inventory_repo.get_by_id(
            target_line_item.inventory_id
        )
        product_id = inventory.product_id

        available_sizes = self._order_service.get_available_sizes_for_product(
            product_id
        )
        available_colors = self._order_service.get_available_colors_for_product(
            product_id
        )

        return {
            "product_name": target_line_item.product_name,
            "current_size": target_line_item.size,
            "current_color": target_line_item.color,
            "current_quantity": target_line_item.quantity,
            "available_sizes": [s["name"] for s in available_sizes],
            "available_colors": [c["name"] for c in available_colors],
        }
