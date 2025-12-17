from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import settings


def main_menu_kb() -> InlineKeyboardMarkup:
    """
    Main menu with WebApp button.
    """
    if not settings.TELEGRAM_WEBAPP_URL:
        url = "https://moonlit-garden-frontend.vercel.app"  # fallback
    else:
        url = str(settings.TELEGRAM_WEBAPP_URL)

    webapp_button = InlineKeyboardButton(
        text="Открыть Лунный сад 🌙",
        web_app=WebAppInfo(url=url),
    )
    return InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])
