from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(default="aegis-api")
    app_version: str = Field(default="0.1.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    api_v1_prefix: str = Field(default="/api/v1")

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)
    database_name: str = Field(default="aegis")
    database_user: str = Field(default="postgres")
    database_password: str = Field(default="postgres")
    
    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    secret_key: str = Field(
        default="change-this-in-production"
    )

    algorithm: str = Field(
        default="HS256"
    )

    access_token_expire_minutes: int = Field(
        default=30
    )
    # ------------------------------------------------------------------
    # AI
    # ------------------------------------------------------------------

    gemini_api_key: str | None = Field(default=None)
    gemini_model: str = Field(default="gemini-2.5-flash")

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy async database URL.
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )
        

@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """
    return Settings()


settings = get_settings()