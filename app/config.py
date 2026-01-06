from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = Field(
        default="Nail Inspo API", description="Service name", env="APP_NAME"
    )
    app_env: str = Field(
        default="development", description="Runtime environment name", env="APP_ENV"
    )
    debug: bool = Field(default=False, description="Enable debug logging", env="DEBUG")
    database_url: str = Field(
        default="sqlite:///./nail_inspo.db",
        description="SQLAlchemy database URL (Postgres recommended in production)",
        env="DATABASE_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
