"""Artwork service for artwork management."""

import uuid

from repositories.artwork_repository import ArtworkRepository
from services.artwork_models import Artwork


class ArtworkService:
    """Business logic for artwork management."""

    def __init__(self, artwork_repo: ArtworkRepository) -> None:
        """Initialize artwork service with required dependencies.

        Args:
            artwork_repo: Repository for artwork data access.
        """
        self._artwork_repo = artwork_repo

    def get_artwork(self, artwork_id: uuid.UUID) -> Artwork:
        """Retrieve an artwork by ID.

        Args:
            artwork_id: UUID of the artwork.

        Returns:
            Artwork model.
        """
        artwork = self._artwork_repo.get_by_id(artwork_id)
        return Artwork.model_validate(artwork)

    def upload_artwork(
        self,
        user_id: uuid.UUID,
        name: str,
        file_url: str,
        file_type: str,
        width_px: int,
        height_px: int,
    ) -> Artwork:
        """Upload a new artwork.

        Args:
            user_id: UUID of the user uploading.
            name: Artwork name.
            file_url: URL of the artwork file.
            file_type: File type.
            width_px: Width in pixels.
            height_px: Height in pixels.

        Returns:
            Created artwork model.
        """
        from db.models import Artwork as ArtworkDB

        artwork = ArtworkDB(
            id=uuid.uuid4(),
            uploaded_by_user_id=user_id,
            name=name,
            file_url=file_url,
            file_type=file_type,
            width_px=width_px,
            height_px=height_px,
            is_active=True,
        )

        created_artwork = self._artwork_repo.create(artwork)
        return Artwork.model_validate(created_artwork)

    def list_user_artworks(self, user_id: uuid.UUID) -> list[Artwork]:
        """List all artworks uploaded by a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of artworks.
        """
        artworks = self._artwork_repo.get_by_user_id(user_id)
        return [Artwork.model_validate(a) for a in artworks]

    def list_active_artworks(self, user_id: uuid.UUID) -> list[Artwork]:
        """List all active artworks for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of active artworks.
        """
        artworks = self._artwork_repo.get_active_by_user_id(user_id)
        return [Artwork.model_validate(a) for a in artworks]

    def deactivate_artwork(self, artwork_id: uuid.UUID) -> Artwork:
        """Deactivate an artwork.

        Args:
            artwork_id: UUID of the artwork.

        Returns:
            Updated artwork model.
        """
        artwork = self._artwork_repo.get_by_id(artwork_id)
        artwork.is_active = False
        updated_artwork = self._artwork_repo.update(artwork)
        return Artwork.model_validate(updated_artwork)
