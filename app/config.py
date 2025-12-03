"""Configuration management for the GAE API service."""
import os
from pydantic_settings import BaseSettings


class RubeEndpoints:
    """
    Centralized configuration for all Rube API endpoints.
    Change these paths when the real Rube REST API is documented.
    """

    # TODO: Update these endpoint paths once Rube REST API docs are available
    # Current values are placeholders for testing
    REPO_SNAPSHOT = "repo/tree"           # Placeholder: GET /repo/tree?project_id=...
    FILE_CONTENT = "repo/file"            # Placeholder: GET /repo/file?project_id=...&path=...

    # TODO: Add additional endpoints as needed:
    # REPO_BRANCHES = "repo/branches"     # Example: GET /repo/branches?project_id=...
    # REPO_COMMITS = "repo/commits"       # Example: GET /repo/commits?project_id=...
    # REPO_DIFF = "repo/diff"             # Example: GET /repo/diff?project_id=...


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Rube service configuration
    rube_base_url: str = os.getenv("RUBE_BASE_URL", "https://rube.example.com")
    rube_api_key: str = os.getenv("RUBE_API_KEY", "")

    # Application settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Optional future settings
    api_key: str | None = None  # For securing this GAE service itself

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Global endpoints configuration
rube_endpoints = RubeEndpoints()
