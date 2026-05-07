"""Application configuration loaded from environment variables / .env file."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = Field(default="", description="Postgres DSN, e.g. postgresql://user:pass@host:5432/db.")

    JWT_SECRET_KEY: str = Field(default="change-me", description="HMAC secret used to sign JWTs.")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRES_MINUTES: int = Field(default=60, ge=1)

    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    PASSWORD_HASH_ITERATIONS: int = Field(default=200_000, ge=10_000)

    LOG_LEVEL: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
