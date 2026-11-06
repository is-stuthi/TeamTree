"""Configuration, read from TeamTree/.env (repo root) or api/.env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", ROOT / "api" / ".env"), extra="ignore"
    )

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "teamtree"
    mysql_root_password: str = ""
    tt_app_password: str = ""
    tt_report_password: str = ""

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    jwt_secret: str = "dev-only-insecure-secret-change-me-please"
    jwt_ttl_minutes: int = 720
    web_origin: str = "http://localhost:3000"
    app_env: str = "development"      # "production" disables /admin/dev/*


@lru_cache
def get_settings() -> Settings:
    return Settings()
