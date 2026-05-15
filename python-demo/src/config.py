"""Configuration module for WhatsApp Scam & Phishing Guardian Agent.

Loads and validates environment variables using pydantic-settings BaseSettings.
"""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources.providers.env import EnvSettingsSource


class _CustomEnvSettingsSource(EnvSettingsSource):
    """Custom env settings source that handles comma-separated lists."""

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        """Override to handle MONITORED_CHAT_IDS as comma-separated string."""
        if field_name == "MONITORED_CHAT_IDS" and isinstance(value, str):
            # Don't try to JSON-parse; let the field_validator handle it
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # WhatsApp API
    WHAPI_TOKEN: str

    # LLM Configuration
    OPENAI_API_KEY: str
    GROQ_API_KEY: str

    # Threat Intelligence APIs
    VIRUSTOTAL_API_KEY: str
    URLSCAN_API_KEY: str

    # Database Configuration
    DATABASE_URL: str = "sqlite:///data/threats.db"

    # WhatsApp Chat Configuration
    MONITORED_CHAT_IDS: list[str] = []
    ADMIN_PHONE_NUMBER: str = ""

    # Application Settings
    LOG_LEVEL: str = "INFO"

    @field_validator("MONITORED_CHAT_IDS", mode="before")
    @classmethod
    def parse_monitored_chat_ids(cls, v: Any) -> list[str]:
        """Parse comma-separated string into a list of chat IDs."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [chat_id.strip() for chat_id in v.split(",") if chat_id.strip()]
        if isinstance(v, list):
            return v
        return []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: Any,
        env_settings: Any,
        dotenv_settings: Any,
        file_secret_settings: Any,
    ) -> tuple[Any, ...]:
        """Use custom env source that handles comma-separated lists."""
        return (
            init_settings,
            _CustomEnvSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
