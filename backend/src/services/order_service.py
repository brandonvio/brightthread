"""Order service with business rules and state machine enforcement."""

import uuid
from datetime import date, timedelta

from repositories.artwork_repository import ArtworkRepository
from repositories.inventory_repository import InventoryRepository
from repositories.order_line_item_repository import OrderLineItemRepository
from repositories.order_repository import OrderRepository
from repositories.order_status_history_repository import OrderStatusHistoryRepository
from repositories.shipping_address_repository import ShippingAddressRepository
from repositories.user_repository import UserRepository
from services.artwork_models import Artwork
from services.order_models import (
    EnrichedOrder,
    EnrichedOrderLineItem,
    Order,
    OrderLineItem,
    OrderStatusHistory,
    OrderSummary,
)
from services.shipping_models import ShippingAddress


class InvalidStateTransitionError(Exception):
    """Raised when attempting invalid order state transition."""

    pass


class InsufficientInventoryError(Exception):
    """Raised when requested quantity exceeds available inventory."""

    pass


class InvalidOrderModificationError(Exception):
    """Raised when modification not allowed in current order state."""

    pass


class OrderValidationError(Exception):
    """Raised when order fails validation rules."""

    pass


class OrderService:
    """Business logic for order lifecycle management."""

    VALID_STATES = ["CREATED", "APPROVED", "IN_PRODUCTION", "READY_TO_SHIP", "SHIPPED"]

    STATE_TRANSITIONS = {
        "CREATED": ["APPROVED"],
        "APPROVED": ["IN_PRODUCTION"],
        "IN_PRODUCTION": ["READY_TO_SHIP"],
        "READY_TO_SHIP": ["SHIPPED"],
        "SHIPPED": [],
    }

    MIN_ORDER_QUANTITY = 10
    MAX_LINE_ITEM_QUANTITY = 500
    MIN_LEAD_TIME_CREATED = 14
    MIN_LEAD_TIME_APPROVED = 12
    MIN_LEAD_TIME_IN_PRODUCTION = 7

    def __init__(
        self,
        order_repo: OrderRepository,
        order_line_item_repo: OrderLineItemRepository,
        inventory_repo: InventoryRepository,
        status_history_repo: OrderStatusHistoryRepository,
        user_repo: UserRepository,
        shipping_repo: ShippingAddressRepository,
        artwork_repo: ArtworkRepository,
    ) -> None:
        """Initialize order service with required dependencies.

        Args:
            order_repo: Repository for order data access.
            order_line_item_repo: Repository for order line item data access.
            inventory_repo: Repository for inventory data access.
            status_history_repo: Repository for order status history data access.
            user_repo: Repository for user data access.
            shipping_repo: Repository for shipping address data access.
            artwork_repo: Repository for artwork data access.
        """
        self._order_repo = order_repo
        self._line_item_repo = order_line_item_repo
        self._inventory_repo = inventory_repo
        self._status_history_repo = status_history_repo
        self._user_repo = user_repo
        self._shipping_repo = shipping_repo
        self._artwork_repo = artwork_repo

    def _build_enriched_line_items(
        self, line_items: list
    ) -> list[EnrichedOrderLineItem]:
        """Build enriched line items with product/size/color details.

        Args:
            line_items: List of SQLAlchemy OrderLineItem models.

        Returns:
            List of enriched order line item models.
        """
        enriched = []
        for item in line_items:
            inventory = self._inventory_repo.get_by_id(item.inventory_id)
            enriched.append(
                EnrichedOrderLineItem(
                    id=item.id,
                    order_id=item.order_id,
                    inventory_id=item.inventory_id,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    product_name=inventory.product.name,
                    product_sku=inventory.product.sku,
                    size=inventory.size.name,
                    color=inventory.color.name,
                    color_hex=inventory.color.hex_code,
                )
            )
        return enriched

    def _build_line_items(self, line_items: list) -> list[OrderLineItem]:
        """Build line item models from SQLAlchemy models.

        Args:
            line_items: List of SQLAlchemy OrderLineItem models.

        Returns:
            List of order line item models.
        """
        return [
            OrderLineItem(
                id=item.id,
                order_id=item.order_id,
                inventory_id=item.inventory_id,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
            )
            for item in line_items
        ]

    def get_order(self, order_id: uuid.UUID) -> Order:
        """Retrieve an order by ID with line items.

        Args:
            order_id: UUID of the order.

        Returns:
            Order model with line items.
        """
        order = self._order_repo.get_by_id(order_id)
        line_items = self._line_item_repo.get_by_order_id(order_id)

        return Order(
            id=order.id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            artwork_id=order.artwork_id,
            status=order.status,
            delivery_date=order.delivery_date,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
            updated_at=order.updated_at,
            line_items=self._build_line_items(line_items),
        )

    def get_enriched_order(self, order_id: uuid.UUID) -> EnrichedOrder:
        """Retrieve a fully enriched order with all related data.

        Args:
            order_id: UUID of the order.

        Returns:
            Enriched order model with user, shipping, artwork, and line item details.
        """
        order = self._order_repo.get_by_id(order_id)
        line_items = self._line_item_repo.get_by_order_id(order_id)
        user = self._user_repo.get_by_id(order.user_id)
        shipping_address = self._shipping_repo.get_by_id(order.shipping_address_id)

        artwork = None
        if order.artwork_id:
            artwork_db = self._artwork_repo.get_by_id(order.artwork_id)
            artwork = Artwork.model_validate(artwork_db)

        return EnrichedOrder(
            id=order.id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            artwork_id=order.artwork_id,
            status=order.status,
            delivery_date=order.delivery_date,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
            updated_at=order.updated_at,
            line_items=self._build_enriched_line_items(line_items),
            user_email=user.email,
            shipping_address=ShippingAddress.model_validate(shipping_address),
            artwork=artwork,
        )

    def get_orders_by_user(self, user_id: uuid.UUID) -> list[OrderSummary]:
        """Retrieve all orders for a user with enriched line items.

        Args:
            user_id: UUID of the user.

        Returns:
            List of order summaries with enriched line items.
        """
        orders = self._order_repo.get_by_user_id(user_id)
        result = []

        for order in orders:
            line_items = self._line_item_repo.get_by_order_id(order.id)
            result.append(
                OrderSummary(
                    id=order.id,
                    user_id=order.user_id,
                    shipping_address_id=order.shipping_address_id,
                    artwork_id=order.artwork_id,
                    status=order.status,
                    delivery_date=order.delivery_date,
                    total_amount=float(order.total_amount),
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    line_items=self._build_enriched_line_items(line_items),
                )
            )

        return result

    def create_order(
        self,
        user_id: uuid.UUID,
        shipping_address_id: uuid.UUID,
        delivery_date: date,
        line_items: list[dict],
        artwork_id: uuid.UUID | None = None,
    ) -> Order:
        """Create a new order with inventory reservation.

        Args:
            user_id: UUID of the user creating the order.
            shipping_address_id: UUID of the shipping address.
            delivery_date: Requested delivery date.
            line_items: List of line items with inventory_id and quantity.
            artwork_id: Optional UUID of artwork.

        Returns:
            Created order with line items.

        Raises:
            OrderValidationError: If order validation fails.
            InsufficientInventoryError: If inventory not available.
        """
        self._validate_order_creation(delivery_date, line_items)
        total_amount = 0.0

        from db.models import Order as OrderDB

        order = OrderDB(
            id=uuid.uuid4(),
            user_id=user_id,
            shipping_address_id=shipping_address_id,
            artwork_id=artwork_id,
            status="CREATED",
            delivery_date=delivery_date,
            total_amount=0.0,
        )
        created_order = self._order_repo.create(order)

        from db.models import OrderLineItem as OrderLineItemDB

        created_line_items = []
        for item in line_items:
            inventory = self._inventory_repo.get_by_id(item["inventory_id"])

            if inventory.available_qty < item["quantity"]:
                raise InsufficientInventoryError(
                    f"Insufficient inventory for {inventory.id}. Available: {inventory.available_qty}, Requested: {item['quantity']}"
                )

            inventory.available_qty -= item["quantity"]
            inventory.reserved_qty += item["quantity"]
            self._inventory_repo.update(inventory)

            line_item = OrderLineItemDB(
                id=uuid.uuid4(),
                order_id=created_order.id,
                inventory_id=item["inventory_id"],
                quantity=item["quantity"],
                unit_price=inventory.product.base_price,
            )
            created_line_item = self._line_item_repo.create(line_item)
            created_line_items.append(created_line_item)
            total_amount += float(line_item.unit_price) * item["quantity"]

        created_order.total_amount = total_amount
        self._order_repo.update(created_order)

        # Record initial status in history
        self._record_status_change(created_order.id, "CREATED")

        return Order(
            id=created_order.id,
            user_id=created_order.user_id,
            shipping_address_id=created_order.shipping_address_id,
            artwork_id=created_order.artwork_id,
            status=created_order.status,
            delivery_date=created_order.delivery_date,
            total_amount=float(created_order.total_amount),
            created_at=created_order.created_at,
            updated_at=created_order.updated_at,
            line_items=self._build_line_items(created_line_items),
        )

    def update_order_status(self, order_id: uuid.UUID, new_status: str) -> Order:
        """Update order status with state machine validation.

        Args:
            order_id: UUID of the order.
            new_status: New status to transition to.

        Returns:
            Updated order.

        Raises:
            InvalidStateTransitionError: If transition is invalid.
        """
        order = self._order_repo.get_by_id(order_id)
        self._validate_state_transition(order.status, new_status)

        order.status = new_status
        updated_order = self._order_repo.update(order)

        # Record status change in history
        self._record_status_change(order_id, new_status)

        line_items = self._line_item_repo.get_by_order_id(order_id)

        return Order(
            id=updated_order.id,
            user_id=updated_order.user_id,
            shipping_address_id=updated_order.shipping_address_id,
            artwork_id=updated_order.artwork_id,
            status=updated_order.status,
            delivery_date=updated_order.delivery_date,
            total_amount=float(updated_order.total_amount),
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            line_items=self._build_line_items(line_items),
        )

    def modify_order(
        self,
        order_id: uuid.UUID,
        shipping_address_id: uuid.UUID | None = None,
        artwork_id: uuid.UUID | None = None,
        delivery_date: date | None = None,
    ) -> Order:
        """Modify order based on current state rules.

        Args:
            order_id: UUID of the order.
            shipping_address_id: New shipping address ID.
            artwork_id: New artwork ID.
            delivery_date: New delivery date.

        Returns:
            Updated order.

        Raises:
            InvalidOrderModificationError: If modification not allowed.
        """
        order = self._order_repo.get_by_id(order_id)
        self._validate_modification(
            order.status, shipping_address_id, artwork_id, delivery_date
        )

        if shipping_address_id is not None:
            order.shipping_address_id = shipping_address_id

        if artwork_id is not None:
            order.artwork_id = artwork_id

        if delivery_date is not None:
            order.delivery_date = delivery_date

        updated_order = self._order_repo.update(order)
        line_items = self._line_item_repo.get_by_order_id(order_id)

        return Order(
            id=updated_order.id,
            user_id=updated_order.user_id,
            shipping_address_id=updated_order.shipping_address_id,
            artwork_id=updated_order.artwork_id,
            status=updated_order.status,
            delivery_date=updated_order.delivery_date,
            total_amount=float(updated_order.total_amount),
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            line_items=self._build_line_items(line_items),
        )

    def cancel_order(self, order_id: uuid.UUID) -> Order:
        """Cancel order and release inventory reservations.

        Args:
            order_id: UUID of the order.

        Returns:
            Cancelled order.

        Raises:
            InvalidOrderModificationError: If cancellation not allowed.
        """
        order = self._order_repo.get_by_id(order_id)

        if order.status in ["READY_TO_SHIP", "SHIPPED"]:
            raise InvalidOrderModificationError(
                f"Cannot cancel order in {order.status} state"
            )

        line_items = self._line_item_repo.get_by_order_id(order_id)

        for line_item in line_items:
            inventory = self._inventory_repo.get_by_id(line_item.inventory_id)
            inventory.available_qty += line_item.quantity
            inventory.reserved_qty -= line_item.quantity
            self._inventory_repo.update(inventory)

        order.status = "CANCELLED"
        updated_order = self._order_repo.update(order)

        # Record cancellation in history
        self._record_status_change(order_id, "CANCELLED")

        return Order(
            id=updated_order.id,
            user_id=updated_order.user_id,
            shipping_address_id=updated_order.shipping_address_id,
            artwork_id=updated_order.artwork_id,
            status=updated_order.status,
            delivery_date=updated_order.delivery_date,
            total_amount=float(updated_order.total_amount),
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            line_items=self._build_line_items(line_items),
        )

    def get_status_history(self, order_id: uuid.UUID) -> list[OrderStatusHistory]:
        """Retrieve status history for an order.

        Args:
            order_id: UUID of the order.

        Returns:
            List of status history entries ordered by transitioned_at.
        """
        history = self._status_history_repo.get_by_order_id(order_id)
        return [OrderStatusHistory.model_validate(h) for h in history]

    def _record_status_change(self, order_id: uuid.UUID, status: str) -> None:
        """Record a status change in the history.

        Args:
            order_id: UUID of the order.
            status: New status value.
        """
        from db.models import OrderStatusHistory as OrderStatusHistoryDB

        history_entry = OrderStatusHistoryDB(
            id=uuid.uuid4(),
            order_id=order_id,
            status=status,
        )
        self._status_history_repo.create(history_entry)

    def _validate_order_creation(
        self, delivery_date: date, line_items: list[dict]
    ) -> None:
        """Validate order creation rules.

        Args:
            delivery_date: Requested delivery date.
            line_items: List of line items.

        Raises:
            OrderValidationError: If validation fails.
        """
        total_quantity = sum(item["quantity"] for item in line_items)

        if total_quantity < self.MIN_ORDER_QUANTITY:
            raise OrderValidationError(
                f"Order must have at least {self.MIN_ORDER_QUANTITY} total items. Found: {total_quantity}"
            )

        for item in line_items:
            if item["quantity"] > self.MAX_LINE_ITEM_QUANTITY:
                raise OrderValidationError(
                    f"Line item quantity cannot exceed {self.MAX_LINE_ITEM_QUANTITY}. Found: {item['quantity']}"
                )

        today = date.today()
        min_delivery_date = today + timedelta(days=self.MIN_LEAD_TIME_CREATED)

        if delivery_date < min_delivery_date:
            raise OrderValidationError(
                f"Delivery date must be at least {self.MIN_LEAD_TIME_CREATED} days from today. Requested: {delivery_date}, Minimum: {min_delivery_date}"
            )

    def _validate_state_transition(self, current_status: str, new_status: str) -> None:
        """Validate state transition is allowed.

        Args:
            current_status: Current order status.
            new_status: Requested new status.

        Raises:
            InvalidStateTransitionError: If transition is invalid.
        """
        if new_status not in self.VALID_STATES:
            raise InvalidStateTransitionError(f"Invalid status: {new_status}")

        allowed_transitions = self.STATE_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_transitions:
            raise InvalidStateTransitionError(
                f"Cannot transition from {current_status} to {new_status}. Allowed: {allowed_transitions}"
            )

    def _validate_modification(
        self,
        current_status: str,
        shipping_address_id: uuid.UUID | None,
        artwork_id: uuid.UUID | None,
        delivery_date: date | None,
    ) -> None:
        """Validate modification is allowed in current state.

        Args:
            current_status: Current order status.
            shipping_address_id: New shipping address ID.
            artwork_id: New artwork ID.
            delivery_date: New delivery date.

        Raises:
            InvalidOrderModificationError: If modification not allowed.
        """
        if current_status == "SHIPPED":
            raise InvalidOrderModificationError(
                "No modifications allowed in SHIPPED state"
            )

        if current_status in ["IN_PRODUCTION", "READY_TO_SHIP"]:
            if artwork_id is not None:
                raise InvalidOrderModificationError(
                    f"Artwork changes not allowed in {current_status} state"
                )

        if current_status == "READY_TO_SHIP":
            if delivery_date is not None:
                raise InvalidOrderModificationError(
                    "Delivery date changes not allowed in READY_TO_SHIP state"
                )

    def modify_line_item(
        self,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID,
        new_quantity: int | None = None,
        new_size_id: uuid.UUID | None = None,
        new_color_id: uuid.UUID | None = None,
    ) -> Order:
        """Modify a line item's quantity, size, or color.

        Args:
            order_id: UUID of the order.
            line_item_id: UUID of the line item to modify.
            new_quantity: New quantity (if changing).
            new_size_id: New size ID (if changing).
            new_color_id: New color ID (if changing).

        Returns:
            Updated order with modified line item.

        Raises:
            InvalidOrderModificationError: If modification not allowed in current state.
            InsufficientInventoryError: If new inventory not available.
        """
        order = self._order_repo.get_by_id(order_id)

        # Note: Status-based validation is handled by the policy tool in the agent layer.
        # The agent evaluates policy before calling this method.

        line_item = self._line_item_repo.get_by_id(line_item_id)
        if line_item.order_id != order_id:
            raise InvalidOrderModificationError(
                f"Line item {line_item_id} does not belong to order {order_id}"
            )

        old_inventory = self._inventory_repo.get_by_id(line_item.inventory_id)
        old_quantity = line_item.quantity

        # Determine if we need new inventory (size/color change)
        needs_new_inventory = new_size_id is not None or new_color_id is not None

        if needs_new_inventory:
            # Find new inventory record
            target_size_id = new_size_id or old_inventory.size_id
            target_color_id = new_color_id or old_inventory.color_id
            target_quantity = new_quantity or old_quantity

            new_inventory = self._inventory_repo.get_by_product_color_size(
                old_inventory.product_id, target_color_id, target_size_id
            )

            # Check availability
            if new_inventory.available_qty < target_quantity:
                raise InsufficientInventoryError(
                    f"Insufficient inventory for new size/color. "
                    f"Available: {new_inventory.available_qty}, Requested: {target_quantity}"
                )

            # Release old inventory reservation
            old_inventory.available_qty += old_quantity
            old_inventory.reserved_qty -= old_quantity
            self._inventory_repo.update(old_inventory)

            # Reserve new inventory
            new_inventory.available_qty -= target_quantity
            new_inventory.reserved_qty += target_quantity
            self._inventory_repo.update(new_inventory)

            # Update line item
            line_item.inventory_id = new_inventory.id
            line_item.quantity = target_quantity
            line_item.unit_price = new_inventory.product.base_price

        elif new_quantity is not None:
            # Just quantity change - same inventory
            quantity_diff = new_quantity - old_quantity

            if quantity_diff > 0:
                # Increasing quantity - check availability
                if old_inventory.available_qty < quantity_diff:
                    raise InsufficientInventoryError(
                        f"Insufficient inventory. "
                        f"Available: {old_inventory.available_qty}, Additional needed: {quantity_diff}"
                    )
                old_inventory.available_qty -= quantity_diff
                old_inventory.reserved_qty += quantity_diff
            else:
                # Decreasing quantity - release inventory
                old_inventory.available_qty -= (
                    quantity_diff  # quantity_diff is negative
                )
                old_inventory.reserved_qty += quantity_diff

            self._inventory_repo.update(old_inventory)
            line_item.quantity = new_quantity

        self._line_item_repo.update(line_item)

        # Recalculate order total
        all_line_items = self._line_item_repo.get_by_order_id(order_id)
        total_amount = sum(
            float(item.unit_price) * item.quantity for item in all_line_items
        )
        order.total_amount = total_amount
        self._order_repo.update(order)

        return Order(
            id=order.id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            artwork_id=order.artwork_id,
            status=order.status,
            delivery_date=order.delivery_date,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
            updated_at=order.updated_at,
            line_items=self._build_line_items(all_line_items),
        )

    def remove_line_item(
        self,
        order_id: uuid.UUID,
        line_item_id: uuid.UUID,
    ) -> Order:
        """Remove a line item from an order.

        Args:
            order_id: UUID of the order.
            line_item_id: UUID of the line item to remove.

        Returns:
            Updated order without the removed line item.

        Raises:
            InvalidOrderModificationError: If removal not allowed.
            OrderValidationError: If removal would leave order below minimum quantity.
        """
        order = self._order_repo.get_by_id(order_id)

        # Note: Status-based validation is handled by the policy tool in the agent layer.
        # The agent evaluates policy before calling this method.

        line_item = self._line_item_repo.get_by_id(line_item_id)
        if line_item.order_id != order_id:
            raise InvalidOrderModificationError(
                f"Line item {line_item_id} does not belong to order {order_id}"
            )

        # Check minimum order quantity after removal
        all_line_items = self._line_item_repo.get_by_order_id(order_id)
        remaining_quantity = sum(
            item.quantity for item in all_line_items if item.id != line_item_id
        )

        if remaining_quantity < self.MIN_ORDER_QUANTITY:
            raise OrderValidationError(
                f"Cannot remove line item. Order must have at least "
                f"{self.MIN_ORDER_QUANTITY} total items. "
                f"Remaining after removal: {remaining_quantity}"
            )

        # Release inventory reservation
        inventory = self._inventory_repo.get_by_id(line_item.inventory_id)
        inventory.available_qty += line_item.quantity
        inventory.reserved_qty -= line_item.quantity
        self._inventory_repo.update(inventory)

        # Delete line item
        self._line_item_repo.delete(line_item)

        # Recalculate order total
        remaining_line_items = [
            item for item in all_line_items if item.id != line_item_id
        ]
        total_amount = sum(
            float(item.unit_price) * item.quantity for item in remaining_line_items
        )
        order.total_amount = total_amount
        self._order_repo.update(order)

        return Order(
            id=order.id,
            user_id=order.user_id,
            shipping_address_id=order.shipping_address_id,
            artwork_id=order.artwork_id,
            status=order.status,
            delivery_date=order.delivery_date,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
            updated_at=order.updated_at,
            line_items=self._build_line_items(remaining_line_items),
        )

    def get_available_sizes_for_product(self, product_id: uuid.UUID) -> list[dict]:
        """Get all available sizes for a product.

        Args:
            product_id: UUID of the product.

        Returns:
            List of size info dicts with id, name, code.
        """
        inventory_items = self._inventory_repo.get_by_product_id(product_id)
        seen_sizes = set()
        sizes = []

        for item in inventory_items:
            if item.size_id not in seen_sizes:
                seen_sizes.add(item.size_id)
                sizes.append(
                    {
                        "id": str(item.size_id),
                        "name": item.size.name,
                        "code": item.size.code,
                    }
                )

        return sizes

    def get_available_colors_for_product(self, product_id: uuid.UUID) -> list[dict]:
        """Get all available colors for a product.

        Args:
            product_id: UUID of the product.

        Returns:
            List of color info dicts with id, name, hex_code.
        """
        inventory_items = self._inventory_repo.get_by_product_id(product_id)
        seen_colors = set()
        colors = []

        for item in inventory_items:
            if item.color_id not in seen_colors:
                seen_colors.add(item.color_id)
                colors.append(
                    {
                        "id": str(item.color_id),
                        "name": item.color.name,
                        "hex_code": item.color.hex_code,
                    }
                )

        return colors
