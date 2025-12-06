# FILE: moonlit_garden_backend/app/bot/handlers.py
from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import start_keyboard
from app.core.config import settings

logger = logging.getLogger(__name__)


def register_handlers(dp: Dispatcher, bot: Bot) -> None:
    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        """
        /start handler with optional deep-link payload.
        Делаем приветствие сразу на русском и английском.
        """
        args = (message.text or "").split(" ", 1)
        payload = args[1] if len(args) > 1 else None

        text = (
            "🌙 Добро пожаловать в Moonlit Garden!\n"
            "Welcome to Moonlit Garden!\n\n"
            "🌿 Это магический сад привычек: отмечайте маленькие шаги — "
            "и растения будут расти под светом луны.\n"
            "🌿 This is a magical habit garden: mark your tiny steps and "
            "watch your plants grow under the moonlight.\n"
        )

        if payload:
            text += (
                "\n\n🔍 Параметр запуска / Deep-link payload:\n"
                f"<code>{payload}</code>"
            )

        await message.answer(text, reply_markup=start_keyboard())

        # Админ-лог / Admin log
        if settings.TELEGRAM_ADMIN_CHAT_ID:
            try:
                await bot.send_message(
                    chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
                    text=(
                        "👤 Новый /start / New /start:\n"
                        f"@{message.from_user.username} ({message.from_user.id})"
                    ),
                )
            except Exception as e:
                logger.warning("Failed to send admin log: %s", e)

    @dp.callback_query(F.data == "about_project")
    async def about_project(callback: CallbackQuery) -> None:
        """
        Краткое описание проекта на двух языках.
        """
        text = (
            "🌿 Moonlit Garden\n\n"
            "RU: Игровой трекер привычек, где каждая привычка — это растение. "
            "Фазы луны, лунная энергия, артефакты и волшебный сад в одном WebApp.\n\n"
            "EN: A gamified habit tracker where every habit is a plant. "
            "Moon phases, lunar energy, artifacts and a magical garden inside one WebApp."
        )
        await callback.message.edit_text(text, reply_markup=start_keyboard())
        await callback.answer()
