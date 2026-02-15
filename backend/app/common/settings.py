from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Coonspect"
    DEBUG: bool = True
    
    MONGO_HOST: str
    MONGO_PORT: int = 27017
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_DB_NAME: str

    @computed_field
    def mongo_url(self) -> str:
        return (
            f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB_NAME}"
            "?authSource=admin"
        )

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_file_encoding="utf-8"
    )

settings = Settings()