"""System endpoints for health checks and API info."""

from datetime import UTC, datetime

from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@router.get("/")
def root() -> dict[str, str]:
    """API information endpoint."""
    logger.info("Root endpoint called")
    return {
        "name": "BrightThread Order Support Agent",
        "version": "0.1.0",
        "description": "Conversational order support system",
    }
