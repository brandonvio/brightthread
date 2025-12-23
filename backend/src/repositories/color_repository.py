"""Color repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Color


class ColorRepository:
    """Data access layer for colors."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Color]:
        """Retrieve all colors from database.

        Returns:
            List of all Color entities.
        """
        return list(self._session.query(Color).order_by(Color.name).all())

    def get_by_id(self, color_id: uuid.UUID) -> Color:
        """Retrieve a color by its ID.

        Args:
            color_id: UUID of the color.

        Returns:
            Color entity.

        Raises:
            NoResultFound: If color does not exist.
        """
        return self._session.query(Color).filter(Color.id == color_id).one()

    def create(self, color: Color) -> Color:
        """Create a new color in the database.

        Args:
            color: Color entity to create.

        Returns:
            Created Color entity.
        """
        self._session.add(color)
        self._session.flush()
        return color

    def count(self) -> int:
        """Count total colors in database.

        Returns:
            Number of colors.
        """
        return self._session.query(Color).count()
