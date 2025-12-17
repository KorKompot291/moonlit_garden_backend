from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from .config import settings

Base = declarative_base()


def get_engine() -> AsyncEngine:
    return create_async_engine(settings.DATABASE_URL, echo=False, future=True)


engine: AsyncEngine = get_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: provide an async DB session.
    """
    async with AsyncSessionLocal() as session:
        yield session
