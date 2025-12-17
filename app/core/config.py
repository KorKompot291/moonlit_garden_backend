from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings, loaded from environment (.env).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App basics ---
    APP_NAME: str = "Moonlit Garden Backend"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    DEFAULT_TIMEZONE: str = "Asia/Phnom_Penh"

    TELEGRAM_WEBAPP_URL: Optional[AnyHttpUrl] = None

    # CORS origins (comma-separated in .env)
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = Field(default_factory=list)

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://moonlit_user:moonlit_password@localhost:5432/moonlit_garden"
    )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Synchronous URL for Alembic (psycopg2).
        """
        if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        return self.DATABASE_URL

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- Telegram bot ---
    TELEGRAM_BOT_TOKEN: str = "8492306440:AAEn5kOgqMCBbGwnUAvXe88odg0uBDY4bwY"
    TELEGRAM_ADMIN_CHAT_ID: Optional[int] = None

    # --- Redis (optional) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Moon logic (can be tuned) ---
    MOON_PHASE_MULTIPLIERS: dict[str, float] = Field(
        default_factory=lambda: {
            "new": 0.9,
            "waxing": 1.1,
            "full": 1.3,
            "waning": 1.0,
        }
    )

    MOON_PHASE_THEME_IDS: dict[str, str] = Field(
        default_factory=lambda: {
            "new": "night_dim",
            "waxing": "night_rising",
            "full": "full_moon_festival",
            "waning": "night_fading",
        }
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
