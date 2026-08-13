"""Application configuration via Pydantic Settings."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://hookline:hookline@localhost:5432/hookline"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    jwt_secret: str = "dev-secret-change-me-min-32-characters"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    api_key_prefix: str = "hl_"

    # Token encryption
    token_encryption_key: str = ""

    # GoHighLevel
    ghl_client_id: str = ""
    ghl_client_secret: str = ""
    ghl_redirect_uri: str = "http://localhost:8000/oauth/ghl/callback"
    ghl_api_base: str = "https://services.leadconnectorhq.com"
    ghl_oauth_base: str = "https://marketplace.leadconnectorhq.com/oauth"

    # Dynamics 365
    dynamics_client_id: str = ""
    dynamics_client_secret: str = ""
    dynamics_tenant_id: str = ""
    dynamics_redirect_uri: str = "http://localhost:8000/oauth/dynamics/callback"
    dynamics_scope: str = "https://org.crm.dynamics.com/.default"
    dynamics_resource_url: str = ""  # org-specific, e.g. https://org.crm.dynamics.com
    dynamics_oauth_base: str = "https://login.microsoftonline.com"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # OpenAI
    openai_api_key: str = ""

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
