"""App settings, read from the project's .env file (never hard-coded)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"  # repo root/.env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV, extra="ignore")

    database_url: str
    enable_scheduler: bool = False


@lru_cache
def get_settings() -> Settings:
    """Load settings once and reuse them."""
    return Settings()
