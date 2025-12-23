"""Size repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Size


class SizeRepository:
    """Data access layer for sizes."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Size]:
        """Retrieve all sizes from database ordered by sort_order.

        Returns:
            List of all Size entities.
        """
        return list(self._session.query(Size).order_by(Size.sort_order).all())

    def get_by_id(self, size_id: uuid.UUID) -> Size:
        """Retrieve a size by its ID.

        Args:
            size_id: UUID of the size.

        Returns:
            Size entity.

        Raises:
            NoResultFound: If size does not exist.
        """
        return self._session.query(Size).filter(Size.id == size_id).one()

    def create(self, size: Size) -> Size:
        """Create a new size in the database.

        Args:
            size: Size entity to create.

        Returns:
            Created Size entity.
        """
        self._session.add(size)
        self._session.flush()
        return size

    def count(self) -> int:
        """Count total sizes in database.

        Returns:
            Number of sizes.
        """
        return self._session.query(Size).count()
