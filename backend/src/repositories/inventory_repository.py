"""Inventory repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Inventory


class InventoryRepository:
    """Data access layer for inventory."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Inventory]:
        """Retrieve all inventory records from database.

        Returns:
            List of all Inventory entities.
        """
        return list(self._session.query(Inventory).all())

    def get_by_id(self, inventory_id: uuid.UUID) -> Inventory:
        """Retrieve an inventory record by its ID.

        Args:
            inventory_id: UUID of the inventory record.

        Returns:
            Inventory entity.

        Raises:
            NoResultFound: If inventory record does not exist.
        """
        return self._session.query(Inventory).filter(Inventory.id == inventory_id).one()

    def get_by_product_color_size(
        self, product_id: uuid.UUID, color_id: uuid.UUID, size_id: uuid.UUID
    ) -> Inventory:
        """Retrieve inventory by product, color, and size combination.

        Args:
            product_id: UUID of the product.
            color_id: UUID of the color.
            size_id: UUID of the size.

        Returns:
            Inventory entity.

        Raises:
            NoResultFound: If inventory record does not exist.
        """
        return (
            self._session.query(Inventory)
            .filter(
                Inventory.product_id == product_id,
                Inventory.color_id == color_id,
                Inventory.size_id == size_id,
            )
            .one()
        )

    def get_by_product_id(self, product_id: uuid.UUID) -> list[Inventory]:
        """Retrieve all inventory records for a product.

        Args:
            product_id: UUID of the product.

        Returns:
            List of Inventory entities.
        """
        return list(
            self._session.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .all()
        )

    def create(self, inventory: Inventory) -> Inventory:
        """Create a new inventory record in the database.

        Args:
            inventory: Inventory entity to create.

        Returns:
            Created Inventory entity.
        """
        self._session.add(inventory)
        self._session.flush()
        return inventory

    def update(self, inventory: Inventory) -> Inventory:
        """Update an inventory record.

        Args:
            inventory: Inventory entity to update.

        Returns:
            Updated Inventory entity.
        """
        self._session.flush()
        return inventory

    def count(self) -> int:
        """Count total inventory records in database.

        Returns:
            Number of inventory records.
        """
        return self._session.query(Inventory).count()
