"""Repository-related endpoints router."""
import logging
from typing import Any
from fastapi import APIRouter, Query, Depends, HTTPException

from app.schemas import RepoSnapshotResponse, FileContentResponse
from app.rube_client import RubeClient, get_rube_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["repository"])


@router.get("/repo-snapshot", response_model=RepoSnapshotResponse)
async def get_repo_snapshot(
    project_id: str = Query(..., description="Project/repository identifier"),
    rube: RubeClient = Depends(get_rube_client)
) -> RepoSnapshotResponse:
    """
    Get repository snapshot with file structure and metadata.

    Args:
        project_id: The project/repo identifier
        rube: Injected Rube client

    Returns:
        RepoSnapshotResponse with file list and metadata

    Raises:
        HTTPException: 400 for bad request, 404 if repo not found, 502/503 if Rube unavailable
    """
    if not project_id or not project_id.strip():
        raise HTTPException(status_code=400, detail="project_id is required")

    logger.info(f"Fetching repo snapshot for project_id={project_id}")

    try:
        snapshot = await rube.get_repo_snapshot(project_id)
        logger.info(f"Successfully fetched snapshot for {project_id}: {len(snapshot.files)} files")
        return snapshot
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error fetching repo snapshot: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/file", response_model=FileContentResponse)
async def get_file_content(
    project_id: str = Query(..., description="Project/repository identifier"),
    path: str = Query(..., description="File path within the repository"),
    rube: RubeClient = Depends(get_rube_client)
) -> FileContentResponse:
    """
    Get file content for a specific path in the repository.

    Args:
        project_id: The project/repo identifier
        path: Relative path to the file
        rube: Injected Rube client

    Returns:
        FileContentResponse with UTF-8 file content

    Raises:
        HTTPException: 400 for bad request, 404 if file not found, 502/503 if Rube unavailable
    """
    if not project_id or not project_id.strip():
        raise HTTPException(status_code=400, detail="project_id is required")

    if not path or not path.strip():
        raise HTTPException(status_code=400, detail="path is required")

    logger.info(f"Fetching file content for project_id={project_id}, path={path}")

    try:
        file_content = await rube.get_file_content(project_id, path)
        logger.info(f"Successfully fetched file {path} from {project_id}")
        return file_content
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error fetching file content: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/debug/rube/ping")
async def debug_rube_ping(
    rube: RubeClient = Depends(get_rube_client)
) -> dict[str, Any]:
    """
    Debug endpoint to test Rube connectivity.

    Performs a lightweight ping to verify:
    - Network connectivity to Rube service
    - Authentication is working
    - Rube can respond with valid JSON

    Args:
        rube: Injected Rube client

    Returns:
        dict with 'ok': true if Rube is reachable

    Raises:
        HTTPException: 503 if cannot reach Rube, 504 on timeout, 502 on other errors
    """
    logger.info("Debug: Testing Rube connectivity")

    try:
        is_reachable = await rube.ping()
        if is_reachable:
            logger.info("Debug: Rube ping successful")
            return {"ok": True}
        else:
            # Should not reach here due to exception raising in ping()
            logger.error("Debug: Rube ping returned False unexpectedly")
            raise HTTPException(status_code=502, detail="Rube ping failed")

    except HTTPException:
        # Re-raise HTTPExceptions from RubeClient (503, 504, 502)
        logger.error("Debug: Rube ping failed with HTTPException")
        raise
    except Exception as exc:
        # Catch any unexpected errors
        logger.error(f"Debug: Unexpected error during Rube ping: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
