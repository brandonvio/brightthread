"""OrderLineItem repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import OrderLineItem


class OrderLineItemRepository:
    """Data access layer for order line items."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[OrderLineItem]:
        """Retrieve all order line items from database.

        Returns:
            List of all OrderLineItem entities.
        """
        return list(self._session.query(OrderLineItem).all())

    def get_by_id(self, line_item_id: uuid.UUID) -> OrderLineItem:
        """Retrieve an order line item by its ID.

        Args:
            line_item_id: UUID of the line item.

        Returns:
            OrderLineItem entity.

        Raises:
            NoResultFound: If line item does not exist.
        """
        return (
            self._session.query(OrderLineItem)
            .filter(OrderLineItem.id == line_item_id)
            .one()
        )

    def get_by_order_id(self, order_id: uuid.UUID) -> list[OrderLineItem]:
        """Retrieve all line items for an order.

        Args:
            order_id: UUID of the order.

        Returns:
            List of OrderLineItem entities.
        """
        return list(
            self._session.query(OrderLineItem)
            .filter(OrderLineItem.order_id == order_id)
            .all()
        )

    def create(self, line_item: OrderLineItem) -> OrderLineItem:
        """Create a new order line item in the database.

        Args:
            line_item: OrderLineItem entity to create.

        Returns:
            Created OrderLineItem entity.
        """
        self._session.add(line_item)
        self._session.flush()
        return line_item

    def update(self, line_item: OrderLineItem) -> OrderLineItem:
        """Update an order line item.

        Args:
            line_item: OrderLineItem entity to update.

        Returns:
            Updated OrderLineItem entity.
        """
        self._session.flush()
        return line_item

    def delete(self, line_item: OrderLineItem) -> None:
        """Delete an order line item.

        Args:
            line_item: OrderLineItem entity to delete.
        """
        self._session.delete(line_item)
        self._session.flush()

    def count(self) -> int:
        """Count total order line items in database.

        Returns:
            Number of order line items.
        """
        return self._session.query(OrderLineItem).count()
