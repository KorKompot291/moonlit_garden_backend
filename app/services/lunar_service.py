from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pytz
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.moon_phases import MoonPhaseInfo, get_moon_phase_for_timezone
from app.models.lunar_energy import LunarEnergyAccount
from app.models.user import User
from app.schemas.lunar import LunarPhaseResponse

_redis_client: Optional[Redis] = None


async def get_redis() -> Optional[Redis]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


async def get_today_lunar_phase(user: User, now: Optional[datetime] = None) -> MoonPhaseInfo:
    if now is None:
        now = datetime.now(tz=timezone.utc)

    tz = pytz.timezone(user.timezone or settings.DEFAULT_TIMEZONE)
    local_dt = now.astimezone(tz)
    local_date = local_dt.date()

    cache_key = f"lunar:{tz.zone}:{local_date.isoformat()}"

    redis = await get_redis()
    if redis:
        cached = await redis.hgetall(cache_key)
        if cached and "phase" in cached:
            return MoonPhaseInfo(
                phase=cached["phase"],  # type: ignore[arg-type]
                age_days=float(cached["age_days"]),
                illumination=float(cached["illumination"]),
                energy_multiplier=float(cached["energy_multiplier"]),
                visual_theme_id=cached["visual_theme_id"],
            )

    info = get_moon_phase_for_timezone(now, tz.zone)

    if redis:
        await redis.hset(
            cache_key,
            mapping={
                "phase": info.phase,
                "age_days": str(info.age_days),
                "illumination": str(info.illumination),
                "energy_multiplier": str(info.energy_multiplier),
                "visual_theme_id": info.visual_theme_id,
            },
        )
        await redis.expire(cache_key, 60 * 60 * 24)

    return info


def lunar_phase_to_response(info: MoonPhaseInfo, user: User, now: Optional[datetime] = None) -> LunarPhaseResponse:
    if now is None:
        now = datetime.now(tz=timezone.utc)

    tz = pytz.timezone(user.timezone or settings.DEFAULT_TIMEZONE)
    local_dt = now.astimezone(tz)
    return LunarPhaseResponse(
        phase=info.phase,
        age_days=info.age_days,
        illumination=info.illumination,
        energy_multiplier=info.energy_multiplier,
        visual_theme_id=info.visual_theme_id,
        local_date=local_dt.date(),
        timezone=tz.zone,
    )


async def get_or_create_energy_account(db: AsyncSession, user: User) -> LunarEnergyAccount:
    stmt = select(LunarEnergyAccount).where(LunarEnergyAccount.user_id == user.id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    if account is None:
        account = LunarEnergyAccount(user_id=user.id, balance=0)
        db.add(account)
        await db.flush()
    return account
