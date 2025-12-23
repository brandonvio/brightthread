"""Catalog endpoints for colors and sizes."""

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.orm import Session

from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.color_repository import ColorRepository
from repositories.size_repository import SizeRepository
from services.catalog_models import Color, Size

router = APIRouter(prefix="/v1/catalog", tags=["BrightThread Catalog"])


@router.get("/colors", response_model=list[Color])
def list_colors(
    auth: AuthenticatedUser,
    session: Session = Depends(get_db_session),
) -> list[Color]:
    """List all available colors."""
    logger.info("GET /v1/catalog/colors")

    color_repo = ColorRepository(session)
    colors = color_repo.get_all()
    return [Color.model_validate(c) for c in colors]


@router.get("/sizes", response_model=list[Size])
def list_sizes(
    auth: AuthenticatedUser,
    session: Session = Depends(get_db_session),
) -> list[Size]:
    """List all available sizes ordered by sort_order."""
    logger.info("GET /v1/catalog/sizes")

    size_repo = SizeRepository(session)
    sizes = size_repo.get_all()
    return [Size.model_validate(s) for s in sizes]
