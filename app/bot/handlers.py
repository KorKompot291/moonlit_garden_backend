from __future__ import annotations

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.bot.keyboards import main_menu_kb
from app.core.config import settings


async def cmd_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в Moonlit Garden 🌙\n\n"
        "Здесь твои привычки превращаются в живой сад с растениями и грибами.\n"
        "Нажми кнопку ниже, чтобы открыть игру.",
        reply_markup=main_menu_kb(),
    )


async def cmd_help(message: Message) -> None:
    await message.answer(
        "Это магический трекер привычек.\n\n"
        "• Открывай WebApp, чтобы управлять садом\n"
        "• Отмечай привычки, выращивай растения и грибы\n"
        "• Собирай артефакты и используй лунную энергию ✨",
        reply_markup=main_menu_kb(),
    )


async def admin_ping(message: Message) -> None:
    if settings.TELEGRAM_ADMIN_CHAT_ID and message.from_user:
        if message.from_user.id == settings.TELEGRAM_ADMIN_CHAT_ID:
            await message.answer("🌿 Bot is alive and connected.")
        else:
            await message.answer("У тебя нет прав администратора.")
    else:
        await message.answer("Администратор не настроен.")


def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(admin_ping, Command("ping"))
