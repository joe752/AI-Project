"""Configuration management for the GAE API service."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All environment variables are defined in app.yaml for GAE deployment.
    For local development, use a .env file or export them in your shell.
    """

    # Application settings
    log_level: str = "INFO"

    # Optional: API key for securing this GAE service itself
    api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_settings() -> Settings:
    """
    Load settings from environment variables.

    Returns:
        Settings instance with configuration
    """
    return Settings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# Global settings instance
settings = load_settings()
