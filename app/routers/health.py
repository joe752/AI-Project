"""Health check endpoint router."""
import logging
from fastapi import APIRouter

from app.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse indicating service is running
    """
    logger.info("Health check requested")
    return HealthResponse(status="ok", service="gae-api")
