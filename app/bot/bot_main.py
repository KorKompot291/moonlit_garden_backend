from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import register_handlers
from app.core.config import settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    register_handlers(dp)

    logging.info("Starting Moonlit Garden bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
