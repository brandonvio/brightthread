"""Artwork repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Artwork


class ArtworkRepository:
    """Data access layer for artworks."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Artwork]:
        """Retrieve all artworks from database.

        Returns:
            List of all Artwork entities.
        """
        return list(
            self._session.query(Artwork).order_by(Artwork.created_at.desc()).all()
        )

    def get_by_id(self, artwork_id: uuid.UUID) -> Artwork:
        """Retrieve an artwork by its ID.

        Args:
            artwork_id: UUID of the artwork.

        Returns:
            Artwork entity.

        Raises:
            NoResultFound: If artwork does not exist.
        """
        return self._session.query(Artwork).filter(Artwork.id == artwork_id).one()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[Artwork]:
        """Retrieve all artworks uploaded by a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of Artwork entities.
        """
        return list(
            self._session.query(Artwork)
            .filter(Artwork.uploaded_by_user_id == user_id)
            .order_by(Artwork.created_at.desc())
            .all()
        )

    def get_active_by_user_id(self, user_id: uuid.UUID) -> list[Artwork]:
        """Retrieve all active artworks uploaded by a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of active Artwork entities.
        """
        return list(
            self._session.query(Artwork)
            .filter(Artwork.uploaded_by_user_id == user_id, Artwork.is_active)
            .order_by(Artwork.created_at.desc())
            .all()
        )

    def create(self, artwork: Artwork) -> Artwork:
        """Create a new artwork in the database.

        Args:
            artwork: Artwork entity to create.

        Returns:
            Created Artwork entity.
        """
        self._session.add(artwork)
        self._session.flush()
        return artwork

    def update(self, artwork: Artwork) -> Artwork:
        """Update an artwork.

        Args:
            artwork: Artwork entity to update.

        Returns:
            Updated Artwork entity.
        """
        self._session.flush()
        return artwork

    def count(self) -> int:
        """Count total artworks in database.

        Returns:
            Number of artworks.
        """
        return self._session.query(Artwork).count()
