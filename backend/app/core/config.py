from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = BACKEND_DIRECTORY / "planer.db"


class Settings(BaseSettings):
    app_name: str = "Planer API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
    hours_per_person_day: Decimal = Decimal("7.7")

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIRECTORY / ".env",
        env_prefix="PLANER_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
