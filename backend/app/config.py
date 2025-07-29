"""
Application configuration using Pydantic settings.

The ``Settings`` class centralises configuration for the application and
reads its values from environment variables.  It covers database
connection details, JWT configuration, Stripe credentials, Celery
settings and other options required by the service.  Defaults are
provided for development convenience but should be overridden via a
``.env`` file or environment variables in production.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import validator



class Settings(BaseSettings):
    """Configuration values loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:q7z9p1m3aGmT@db:5432/raizdigital"

    # Security
    secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day

    # Stripe integration
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: Optional[str] = None

    # Celery / Redis
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # Internal API key for robot to submit results
    internal_api_key: str = "CHANGE_ME_INTERNAL"

    # API
    api_base_url: str = "http://backend:8000"

    # Frontend base URL used when constructing links sent in emails
    # such as password reset or order status notifications. In
    # production, set this to the publicly accessible URL of your
    # frontend application (e.g., https://app.raizdigital.com).
    frontend_base_url: str = "http://localhost:5173"

    # Email configuration (for sending notifications). Replace these
    # with the credentials from your transactional email provider.  If
    # left empty, the application will log email contents instead of
    # sending them.
    email_sender: str = "no-reply@raizdigital.com"
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    @validator("celery_broker_url", pre=True, always=True)
    def set_celery_broker(cls, v, values):  # type: ignore[override]
        """Ensure Celery broker URL defaults to Redis if not explicitly set."""
        return v or values.get("redis_url")

    @validator("celery_result_backend", pre=True, always=True)
    def set_celery_result_backend(cls, v, values):  # type: ignore[override]
        """Ensure Celery result backend defaults to Redis if not explicitly set."""
        return v or values.get("redis_url")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using ``lru_cache`` here ensures that the Settings object is only
    instantiated once which avoids repeatedly parsing environment
    variables and improves performance.
    """
    return Settings()
