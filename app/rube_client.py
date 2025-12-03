"""
HTTP client for communicating with Rube REST API.

All Rube endpoint paths are configured in app.config.RubeEndpoints.
Authentication uses RUBE_API_KEY via Bearer token.
"""

import logging
from typing import Optional

import httpx
from fastapi import HTTPException

from app.config import settings, rube_endpoints
from app.schemas import FileMetadata, RepoSnapshotResponse, FileContentResponse

logger = logging.getLogger(__name__)


class RubeClient:
    """
    Async HTTP client for calling Rube's REST API.

    Features:
    - Centralized endpoint configuration via app.config.RubeEndpoints
    - Bearer token authentication using RUBE_API_KEY
    - Clean error mapping to FastAPI HTTPException
    - All Rube URLs configured in one place for easy maintenance
    """

    def __init__(self):
        """Initialize the Rube client with configuration from settings."""
        self.base_url = settings.rube_base_url
        self.api_key = settings.rube_api_key

        if not self.base_url:
            raise RuntimeError("RUBE_BASE_URL environment variable is not set")
        if not self.api_key:
            logger.warning("RUBE_API_KEY is not set - authentication may fail")

        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"RubeClient initialized with base_url: {self.base_url}")

    async def close(self):
        """Close the HTTP client and clean up resources."""
        await self.client.aclose()
        logger.info("RubeClient closed")

    async def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Internal helper for GET requests to Rube.

        Args:
            endpoint: API endpoint path (from rube_endpoints config)
            params: Optional query parameters

        Returns:
            JSON response as dict

        Raises:
            HTTPException: Mapped from Rube errors with appropriate status codes
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        logger.debug(f"Calling Rube: GET {url} with params={params}")

        try:
            resp = await self.client.get(url, params=params, headers=headers)
        except httpx.TimeoutException as exc:
            logger.error(f"Timeout calling Rube at {url}: {exc}")
            raise HTTPException(
                status_code=504,
                detail="Rube service timeout"
            )
        except httpx.RequestError as exc:
            logger.error(f"Connection error calling Rube at {url}: {exc}")
            raise HTTPException(
                status_code=503,
                detail="Cannot reach Rube service"
            )

        # Map Rube HTTP errors to appropriate FastAPI exceptions
        return self._handle_response(resp, url)

    def _handle_response(self, resp: httpx.Response, url: str) -> dict:
        """
        Map Rube response codes to FastAPI HTTPException.

        Args:
            resp: HTTP response from Rube
            url: The URL that was called (for logging)

        Returns:
            JSON response body as dict

        Raises:
            HTTPException: With appropriate status code and detail message
        """
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError as exc:
                logger.error(f"Invalid JSON from Rube at {url}: {exc}")
                raise HTTPException(
                    status_code=502,
                    detail="Invalid response from Rube service"
                )

        # Error responses
        error_detail = self._extract_error_detail(resp)

        if resp.status_code == 401:
            logger.error(f"Authentication failed with Rube: {error_detail}")
            raise HTTPException(
                status_code=502,
                detail="Rube authentication failed (check RUBE_API_KEY)"
            )
        elif resp.status_code == 404:
            logger.warning(f"Resource not found on Rube: {url}")
            raise HTTPException(
                status_code=404,
                detail=error_detail or "Resource not found"
            )
        elif resp.status_code >= 500:
            logger.error(f"Rube server error ({resp.status_code}): {error_detail}")
            raise HTTPException(
                status_code=502,
                detail=f"Rube service error: {error_detail}"
            )
        elif resp.status_code >= 400:
            logger.warning(f"Bad request to Rube ({resp.status_code}): {error_detail}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {error_detail}"
            )
        else:
            logger.error(f"Unexpected response from Rube ({resp.status_code})")
            raise HTTPException(
                status_code=502,
                detail="Unexpected response from Rube service"
            )

    def _extract_error_detail(self, resp: httpx.Response) -> str:
        """
        Try to extract error message from Rube response.

        Args:
            resp: HTTP response from Rube

        Returns:
            Error message string or generic fallback
        """
        try:
            data = resp.json()
            # Try common error message fields
            return data.get("error") or data.get("message") or data.get("detail") or str(data)
        except ValueError:
            # Not JSON, try to use text
            text = resp.text[:200]  # Limit error text length
            return text if text else f"HTTP {resp.status_code}"

    # -------------------------------------------------------------------------
    # Public API Methods
    # -------------------------------------------------------------------------
    # All endpoint paths come from app.config.rube_endpoints for easy changes

    async def get_repo_snapshot(self, project_id: str) -> RepoSnapshotResponse:
        """
        Get repository file tree/snapshot from Rube.

        TODO: Verify this endpoint path with Rube REST API documentation.
        Currently using placeholder: GET /repo/tree?project_id=...

        Args:
            project_id: Repository identifier

        Returns:
            RepoSnapshotResponse with file list and metadata

        Raises:
            HTTPException: If Rube request fails
        """
        # TODO: Update rube_endpoints.REPO_SNAPSHOT when real API is documented
        data = await self._get(
            rube_endpoints.REPO_SNAPSHOT,
            params={"project_id": project_id}
        )

        # Transform Rube response to our schema
        # TODO: Adjust field mapping based on actual Rube response structure
        files = [
            FileMetadata(
                path=f.get("path", ""),
                type=f.get("type", "file"),
                size=f.get("size"),
                sha=f.get("sha"),
            )
            for f in data.get("files", [])
        ]

        return RepoSnapshotResponse(
            project_id=project_id,
            files=files,
            commit_info=data.get("commit_info"),
        )

    async def get_file_content(self, project_id: str, path: str) -> FileContentResponse:
        """
        Get file content from Rube.

        TODO: Verify this endpoint path with Rube REST API documentation.
        Currently using placeholder: GET /repo/file?project_id=...&path=...

        Args:
            project_id: Repository identifier
            path: File path within repository

        Returns:
            FileContentResponse with file content

        Raises:
            HTTPException: If Rube request fails
        """
        # TODO: Update rube_endpoints.FILE_CONTENT when real API is documented
        data = await self._get(
            rube_endpoints.FILE_CONTENT,
            params={"project_id": project_id, "path": path}
        )

        # TODO: Adjust field mapping based on actual Rube response structure
        return FileContentResponse(
            project_id=project_id,
            path=path,
            content=data.get("content", ""),
            encoding=data.get("encoding", "utf-8"),
            size=data.get("size"),
        )


# -------------------------------------------------------------------------
# Global instance for FastAPI dependency injection
# -------------------------------------------------------------------------

rube_client: Optional[RubeClient] = None


def get_rube_client() -> RubeClient:
    """
    FastAPI dependency to get the global RubeClient instance.

    Returns:
        RubeClient instance

    Raises:
        RuntimeError: If client not initialized in main.py
    """
    if not rube_client:
        raise RuntimeError("RubeClient not initialized in main.py")
    return rube_client
