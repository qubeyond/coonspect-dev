import os
import sys
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coonspect"
    DEBUG: bool = False

    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "base"
    MONGO_PASS: str = "base"
    MONGO_DB_NAME: str = "coonspect"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @computed_field
    def mongo_url(self) -> str:
        return (
            f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB_NAME}"
            "?authSource=admin"
        )

    @computed_field
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    _env_name = (
        ".env.test"
        if "pytest" in sys.modules or os.getenv("PYTEST_CURRENT_TEST")
        else ".env"
    )
    _env_path = BASE_DIR.parent / _env_name

    model_config = SettingsConfigDict(
        env_file=str(_env_path), extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()
