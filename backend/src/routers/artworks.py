"""Artwork management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import CreateArtworkRequest, UpdateArtworkRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.artwork_repository import ArtworkRepository
from services.artwork_models import Artwork
from services.artwork_service import ArtworkService

router = APIRouter(prefix="/v1/artworks", tags=["BrightThread Artworks"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class ArtworkListResponse(BaseModel):
    """Response for list of artworks."""

    artworks: list[Artwork]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_artwork_service(session: Session = Depends(get_db_session)) -> ArtworkService:
    """Create ArtworkService with injected dependencies."""
    artwork_repo = ArtworkRepository(session)
    return ArtworkService(artwork_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=ArtworkListResponse)
def list_artworks(
    auth: AuthenticatedUser,
    artwork_service: ArtworkService = Depends(get_artwork_service),
) -> ArtworkListResponse:
    """List all artworks for the authenticated user."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"GET /v1/artworks - user_id: {user_id}")

    artworks = artwork_service.list_user_artworks(user_id)
    return ArtworkListResponse(artworks=artworks, total=len(artworks))


@router.get("/active", response_model=ArtworkListResponse)
def list_active_artworks(
    auth: AuthenticatedUser,
    artwork_service: ArtworkService = Depends(get_artwork_service),
) -> ArtworkListResponse:
    """List all active artworks for the authenticated user."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"GET /v1/artworks/active - user_id: {user_id}")

    artworks = artwork_service.list_active_artworks(user_id)
    return ArtworkListResponse(artworks=artworks, total=len(artworks))


@router.get("/{artwork_id}", response_model=Artwork)
def get_artwork(
    artwork_id: str,
    auth: AuthenticatedUser,
    artwork_service: ArtworkService = Depends(get_artwork_service),
) -> Artwork:
    """Get artwork by ID."""
    logger.info(f"GET /v1/artworks/{artwork_id}")

    artwork_uuid = uuid.UUID(artwork_id)
    return artwork_service.get_artwork(artwork_uuid)


@router.post("", response_model=Artwork, status_code=201)
def upload_artwork(
    request: CreateArtworkRequest,
    auth: AuthenticatedUser,
    artwork_service: ArtworkService = Depends(get_artwork_service),
) -> Artwork:
    """Upload a new artwork."""
    user_id = uuid.UUID(auth.user_id)
    logger.info(f"POST /v1/artworks - user_id: {user_id}")

    return artwork_service.upload_artwork(
        user_id=user_id,
        name=request.name,
        file_url=request.file_url,
        file_type=request.file_type,
        width_px=request.width_px,
        height_px=request.height_px,
    )


@router.patch("/{artwork_id}", response_model=Artwork)
def update_artwork(
    artwork_id: str,
    request: UpdateArtworkRequest,
    auth: AuthenticatedUser,
    artwork_service: ArtworkService = Depends(get_artwork_service),
) -> Artwork:
    """Update artwork (deactivate/activate)."""
    logger.info(f"PATCH /v1/artworks/{artwork_id}")

    artwork_uuid = uuid.UUID(artwork_id)

    if not request.is_active:
        return artwork_service.deactivate_artwork(artwork_uuid)
    else:
        return artwork_service.get_artwork(artwork_uuid)
