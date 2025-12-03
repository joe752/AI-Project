"""Repository-related endpoints router (placeholder)."""
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["repository"])


@router.get("/info")
async def api_info():
    """
    Placeholder endpoint for future repository API.

    Returns:
        dict: Information about the API status
    """
    logger.info("API info endpoint called")
    return {
        "message": "Repository API not implemented yet",
        "status": "placeholder",
        "version": "1.0.0"
    }
