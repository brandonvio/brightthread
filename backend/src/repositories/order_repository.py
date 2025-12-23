"""Order repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Order


class OrderRepository:
    """Data access layer for orders."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Order]:
        """Retrieve all orders from database.

        Returns:
            List of all Order entities.
        """
        return list(self._session.query(Order).order_by(Order.created_at.desc()).all())

    def get_by_id(self, order_id: uuid.UUID) -> Order:
        """Retrieve an order by its ID.

        Args:
            order_id: UUID of the order.

        Returns:
            Order entity.

        Raises:
            NoResultFound: If order does not exist.
        """
        return self._session.query(Order).filter(Order.id == order_id).one()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[Order]:
        """Retrieve all orders for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of Order entities.
        """
        return list(
            self._session.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_by_status(self, status: str) -> list[Order]:
        """Retrieve all orders with a specific status.

        Args:
            status: Order status.

        Returns:
            List of Order entities.
        """
        return list(
            self._session.query(Order)
            .filter(Order.status == status)
            .order_by(Order.created_at.desc())
            .all()
        )

    def create(self, order: Order) -> Order:
        """Create a new order in the database.

        Args:
            order: Order entity to create.

        Returns:
            Created Order entity.
        """
        self._session.add(order)
        self._session.flush()
        return order

    def update(self, order: Order) -> Order:
        """Update an order.

        Args:
            order: Order entity to update.

        Returns:
            Updated Order entity.
        """
        self._session.flush()
        return order

    def count(self) -> int:
        """Count total orders in database.

        Returns:
            Number of orders.
        """
        return self._session.query(Order).count()
