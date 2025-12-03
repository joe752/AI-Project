"""Configuration management for the GAE API service."""
import os
import sys
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
    """
    Application settings loaded from environment variables.

    All environment variables are defined in app.yaml for GAE deployment.
    For local development, use a .env file or export them in your shell.
    """

    # Rube service configuration (REQUIRED)
    rube_base_url: str
    rube_api_key: str

    # Application settings (optional with defaults)
    log_level: str = "INFO"

    # Optional future settings
    api_key: str | None = None  # For securing this GAE service itself

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        """Initialize settings and validate required environment variables."""
        super().__init__(**kwargs)
        self._validate_required_vars()

    def _validate_required_vars(self):
        """Validate that all required environment variables are set."""
        missing_vars = []

        if not self.rube_base_url or self.rube_base_url == "":
            missing_vars.append("RUBE_BASE_URL")

        if not self.rube_api_key or self.rube_api_key == "":
            missing_vars.append("RUBE_API_KEY")

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please set them in:\n"
                f"  - app.yaml (for GAE deployment)\n"
                f"  - .env file (for local development)\n"
                f"  - Or export them in your shell"
            )
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)


def load_settings() -> Settings:
    """
    Load and validate settings from environment variables.

    Returns:
        Settings instance with validated configuration

    Raises:
        ValueError: If required environment variables are missing
    """
    return Settings(
        rube_base_url=os.getenv("RUBE_BASE_URL", ""),
        rube_api_key=os.getenv("RUBE_API_KEY", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# Global settings instance (will raise ValueError if required vars missing)
settings = load_settings()

# Global endpoints configuration
rube_endpoints = RubeEndpoints()
