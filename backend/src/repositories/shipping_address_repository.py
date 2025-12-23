"""ShippingAddress repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import ShippingAddress


class ShippingAddressRepository:
    """Data access layer for shipping addresses."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[ShippingAddress]:
        """Retrieve all shipping addresses from database.

        Returns:
            List of all ShippingAddress entities.
        """
        return list(
            self._session.query(ShippingAddress)
            .order_by(ShippingAddress.created_at.desc())
            .all()
        )

    def get_by_id(self, address_id: uuid.UUID) -> ShippingAddress:
        """Retrieve a shipping address by its ID.

        Args:
            address_id: UUID of the shipping address.

        Returns:
            ShippingAddress entity.

        Raises:
            NoResultFound: If shipping address does not exist.
        """
        return (
            self._session.query(ShippingAddress)
            .filter(ShippingAddress.id == address_id)
            .one()
        )

    def get_by_user_id(self, user_id: uuid.UUID) -> list[ShippingAddress]:
        """Retrieve all shipping addresses created by a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of ShippingAddress entities.
        """
        return list(
            self._session.query(ShippingAddress)
            .filter(ShippingAddress.created_by_user_id == user_id)
            .order_by(
                ShippingAddress.is_default.desc(), ShippingAddress.created_at.desc()
            )
            .all()
        )

    def get_default_by_user_id(self, user_id: uuid.UUID) -> ShippingAddress:
        """Retrieve the default shipping address for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            Default ShippingAddress entity.

        Raises:
            NoResultFound: If no default address exists.
        """
        return (
            self._session.query(ShippingAddress)
            .filter(
                ShippingAddress.created_by_user_id == user_id,
                ShippingAddress.is_default,
            )
            .one()
        )

    def create(self, address: ShippingAddress) -> ShippingAddress:
        """Create a new shipping address in the database.

        Args:
            address: ShippingAddress entity to create.

        Returns:
            Created ShippingAddress entity.
        """
        self._session.add(address)
        self._session.flush()
        return address

    def update(self, address: ShippingAddress) -> ShippingAddress:
        """Update a shipping address.

        Args:
            address: ShippingAddress entity to update.

        Returns:
            Updated ShippingAddress entity.
        """
        self._session.flush()
        return address

    def count(self) -> int:
        """Count total shipping addresses in database.

        Returns:
            Number of shipping addresses.
        """
        return self._session.query(ShippingAddress).count()
