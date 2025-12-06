from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # application
    APP_NAME: str
    APP_LAYER: str
    APP_ENVIRONMENT: str
    LOG_LEVEL: str
    LOG_FILE_PATH: str
    CORS_ALLOWED_ORIGINS: str
    FRONTEND_REDIRECT_URL: str

    # google oauth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Database
    DATABASE_URL: str

    # security
    APP_SESSION_SECRET_KEY: str
    APP_JWT_ALGORITHM: str = "HS256"
    APP_JWT_EXPIRY_MINUTES: int = 60
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_SAMESITE: str = "lax"

    # debug
    BACKDOOR_SECRET_KEY: str = "dev_key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
