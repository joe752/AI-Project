"""HTTP client for communicating with Rube service."""
import logging
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings
from app.schemas import FileMetadata, RepoSnapshotResponse, FileContentResponse

logger = logging.getLogger(__name__)


class RubeClient:
    """Client for making HTTP requests to Rube service."""

    def __init__(self, base_url: str | None = None):
        """Initialize Rube client with base URL."""
        self.base_url = base_url or settings.rube_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_repo_snapshot(self, project_id: str) -> RepoSnapshotResponse:
        """
        Get repository snapshot from Rube.

        Args:
            project_id: Project/repo identifier

        Returns:
            RepoSnapshotResponse with file list and metadata

        Raises:
            HTTPException: If Rube request fails
        """
        url = f"{self.base_url}/repos/{project_id}/snapshot"
        logger.info(f"Requesting repo snapshot from Rube: {url}")

        try:
            response = await self.client.get(url)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Repository '{project_id}' not found")
            elif response.status_code >= 500:
                raise HTTPException(status_code=502, detail="Rube service unavailable")
            elif response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail="Bad request to Rube")

            response.raise_for_status()
            data = response.json()

            # Transform Rube response to our schema
            files = [
                FileMetadata(
                    path=f.get("path", ""),
                    type=f.get("type", "file"),
                    size=f.get("size"),
                    sha=f.get("sha")
                )
                for f in data.get("files", [])
            ]

            return RepoSnapshotResponse(
                project_id=project_id,
                files=files,
                commit_info=data.get("commit_info")
            )

        except httpx.RequestError as exc:
            logger.error(f"Failed to connect to Rube: {exc}")
            raise HTTPException(status_code=503, detail="Unable to connect to Rube service")

    async def get_file_content(self, project_id: str, path: str) -> FileContentResponse:
        """
        Get file content from Rube.

        Args:
            project_id: Project/repo identifier
            path: File path within the repository

        Returns:
            FileContentResponse with file content

        Raises:
            HTTPException: If Rube request fails
        """
        url = f"{self.base_url}/repos/{project_id}/files"
        params = {"path": path}
        logger.info(f"Requesting file content from Rube: {url}?path={path}")

        try:
            response = await self.client.get(url, params=params)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"File '{path}' not found in repository '{project_id}'")
            elif response.status_code >= 500:
                raise HTTPException(status_code=502, detail="Rube service unavailable")
            elif response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail="Bad request to Rube")

            response.raise_for_status()
            data = response.json()

            return FileContentResponse(
                project_id=project_id,
                path=path,
                content=data.get("content", ""),
                encoding=data.get("encoding", "utf-8"),
                size=data.get("size")
            )

        except httpx.RequestError as exc:
            logger.error(f"Failed to connect to Rube: {exc}")
            raise HTTPException(status_code=503, detail="Unable to connect to Rube service")


# Global client instance (will be initialized in main.py)
rube_client: RubeClient | None = None


def get_rube_client() -> RubeClient:
    """Dependency function to get Rube client instance."""
    if rube_client is None:
        raise RuntimeError("Rube client not initialized")
    return rube_client
