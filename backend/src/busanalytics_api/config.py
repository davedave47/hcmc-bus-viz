"""Runtime settings (12-factor: env-overridable)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BUSAPI_", env_file=".env")

    db_path: str = "db/bus.duckdb"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
