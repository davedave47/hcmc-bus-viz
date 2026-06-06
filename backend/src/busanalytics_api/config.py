"""Runtime settings (12-factor: env-overridable)."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> busanalytics_api -> src -> backend -> <repo root>
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BUSAPI_", env_file=".env")

    # Read-only warehouse the API serves from. DuckDB today; the BigQuery swap
    # is localised to db.py + the repositories (see spec §3.2).
    db_path: str = str(_REPO_ROOT / "db" / "bus.duckdb")
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
