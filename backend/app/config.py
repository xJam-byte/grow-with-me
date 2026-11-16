from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_name: str = "Grow With Me API"
    secret_key: str = "grow-with-me-dev-secret-key-replace-in-production"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_mini_app_url: str = "http://localhost:5173"
    owner_telegram_id: int | None = None
    telegram_webhook_secret: str = ""
    telegram_webhook_url: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5433/grow_with_me"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens_per_day: int = 50000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_dev(self) -> bool:
        return self.app_env.lower() in ("dev", "development", "local")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
