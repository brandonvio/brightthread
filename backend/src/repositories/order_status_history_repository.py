"""Order status history repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import OrderStatusHistory


class OrderStatusHistoryRepository:
    """Data access layer for order status history."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_by_order_id(self, order_id: uuid.UUID) -> list[OrderStatusHistory]:
        """Retrieve all status history entries for an order.

        Args:
            order_id: UUID of the order.

        Returns:
            List of OrderStatusHistory entities ordered by transitioned_at.
        """
        return list(
            self._session.query(OrderStatusHistory)
            .filter(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.transitioned_at.asc())
            .all()
        )

    def create(self, status_history: OrderStatusHistory) -> OrderStatusHistory:
        """Create a new status history entry.

        Args:
            status_history: OrderStatusHistory entity to create.

        Returns:
            Created OrderStatusHistory entity.
        """
        self._session.add(status_history)
        self._session.flush()
        return status_history

    def get_latest_by_order_id(self, order_id: uuid.UUID) -> OrderStatusHistory | None:
        """Retrieve the most recent status history entry for an order.

        Args:
            order_id: UUID of the order.

        Returns:
            Most recent OrderStatusHistory entity or None if no history exists.
        """
        return (
            self._session.query(OrderStatusHistory)
            .filter(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.transitioned_at.desc())
            .first()
        )
