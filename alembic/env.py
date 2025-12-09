from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base
from app.models import *  # noqa

# Alembic config
config = context.config

# Устанавливаем правильный async URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Логирование Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Мета-информация моделей
target_metadata = Base.metadata


def get_url():
    """Получаем URL подключения."""
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline():
    """Запуск миграций без подключения к БД (offline)."""
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Реальное выполнение миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Асинхронный запуск миграций."""
    url = get_url()

    connectable: AsyncEngine = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Выбор режима offline/online
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
