"""Configuration management for the GAE API service."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    rube_base_url: str = os.getenv("RUBE_BASE_URL", "https://rube.example.com")

    # Optional future settings
    api_key: str | None = None
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
