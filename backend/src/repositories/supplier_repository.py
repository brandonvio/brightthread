"""Supplier repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Supplier


class SupplierRepository:
    """Data access layer for suppliers."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Supplier]:
        """Retrieve all suppliers from database.

        Returns:
            List of all Supplier entities.
        """
        return list(self._session.query(Supplier).order_by(Supplier.name).all())

    def get_by_id(self, supplier_id: uuid.UUID) -> Supplier:
        """Retrieve a supplier by its ID.

        Args:
            supplier_id: UUID of the supplier.

        Returns:
            Supplier entity.

        Raises:
            NoResultFound: If supplier does not exist.
        """
        return self._session.query(Supplier).filter(Supplier.id == supplier_id).one()

    def create(self, supplier: Supplier) -> Supplier:
        """Create a new supplier in the database.

        Args:
            supplier: Supplier entity to create.

        Returns:
            Created Supplier entity.
        """
        self._session.add(supplier)
        self._session.flush()
        return supplier

    def count(self) -> int:
        """Count total suppliers in database.

        Returns:
            Number of suppliers.
        """
        return self._session.query(Supplier).count()
