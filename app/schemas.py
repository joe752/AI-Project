"""Pydantic models for request/response schemas."""
from typing import Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Human-readable error message")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Service health status")
    service: str = Field(default="gae-api", description="Service name")


class FileMetadata(BaseModel):
    """Metadata for a single file in the repo."""

    path: str = Field(..., description="Relative path to the file")
    type: str = Field(..., description="Type of entry: 'file' or 'dir'")
    size: int | None = Field(None, description="File size in bytes (if applicable)")
    sha: str | None = Field(None, description="Git SHA or hash (if available)")


class RepoSnapshotResponse(BaseModel):
    """Response for repo snapshot endpoint."""

    project_id: str = Field(..., description="Project/repo identifier")
    files: list[FileMetadata] = Field(default_factory=list, description="List of files and directories")
    commit_info: dict[str, Any] | None = Field(None, description="Optional recent commit information")


class FileContentResponse(BaseModel):
    """Response for file content endpoint."""

    project_id: str = Field(..., description="Project/repo identifier")
    path: str = Field(..., description="File path")
    content: str = Field(..., description="UTF-8 encoded file content")
    encoding: str = Field(default="utf-8", description="Content encoding")
    size: int | None = Field(None, description="File size in bytes")
