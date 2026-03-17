from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # application
    APP_NAME: str = "FastAPI Framework"
    APP_LAYER: str = "api"
    APP_ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    CORS_ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value):
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return ["*"]
            return [item.strip() for item in raw.split(",") if item.strip()]
        return value


settings = Settings()
