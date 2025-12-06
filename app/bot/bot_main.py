from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import register_handlers
from app.core.config import settings


async def main() -> None:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    register_handlers(dp, bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
