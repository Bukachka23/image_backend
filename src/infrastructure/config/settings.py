from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    gemini_api_key: str | None = None
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    # Database
    database_url: str = "sqlite:///./credits.db"

    # URLs
    frontend_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] = ["*"]

    # Business Rules
    credits_per_generation: int = 3

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment
    environment: str = "development"
    debug: bool = False

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def initialize_settings() -> Settings:
    """Initialize settings (useful for testing)"""
    global _settings
    _settings = Settings()
    return _settings
