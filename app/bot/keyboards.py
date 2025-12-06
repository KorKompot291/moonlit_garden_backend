# FILE: moonlit_garden_backend/app/bot/keyboards.py
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import settings


def start_keyboard() -> InlineKeyboardMarkup:
    """
    Стартовая клавиатура:
    - Кнопка WebApp с подписью на русском и английском
    - Кнопка "о проекте" тоже двуязычная
    """
    buttons: list[list[InlineKeyboardButton]] = []

    if settings.TELEGRAM_WEBAPP_URL:
        # Можно прокинуть язык как query-параметр ?lang=ru|en, если фронтенд будет это учитывать.
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🌙 Открыть Moonlit Garden / Open Moonlit Garden",
                    web_app=WebAppInfo(url=str(settings.TELEGRAM_WEBAPP_URL)),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="ℹ️ О проекте / About",
                callback_data="about_project",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
