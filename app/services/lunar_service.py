from __future__ import annotations

from datetime import date, datetime
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.moon_phases import MoonPhaseInfo, get_moon_phase_info
from app.models.lunar_energy import LunarEnergyAccount
from app.schemas.lunar import LunarEnergyOut


async def get_or_create_lunar_account(db: AsyncSession, user_id: int) -> LunarEnergyAccount:
    result = await db.execute(
        select(LunarEnergyAccount).where(LunarEnergyAccount.user_id == user_id)
    )
    acc = result.scalar_one_or_none()
    if not acc:
        acc = LunarEnergyAccount(user_id=user_id, balance=0)
        db.add(acc)
        await db.commit()
        await db.refresh(acc)
    return acc


def get_today_moon_phase(dt: datetime | None = None) -> MoonPhaseInfo:
    if dt is None:
        dt = datetime.utcnow()
    return get_moon_phase_info(dt)


async def get_lunar_energy(db: AsyncSession, user_id: int) -> LunarEnergyOut:
    acc = await get_or_create_lunar_account(db, user_id)
    return LunarEnergyOut(
        balance=acc.balance,
        last_daily_bonus_date=acc.last_daily_bonus_date,
    )


async def apply_lunar_energy_change(
    db: AsyncSession,
    user_id: int,
    delta: int,
) -> LunarEnergyAccount:
    acc = await get_or_create_lunar_account(db, user_id)
    acc.balance += delta
    if acc.balance < 0:
        acc.balance = 0
    await db.commit()
    await db.refresh(acc)
    return acc


async def apply_daily_bonus(
    db: AsyncSession,
    user_id: int,
    today: date,
) -> Tuple[bool, LunarEnergyAccount, int]:
    """
    Returns (applied, account, amount).
    """
    acc = await get_or_create_lunar_account(db, user_id)
    if acc.last_daily_bonus_date == today:
        return False, acc, 0

    phase_info = get_today_moon_phase()
    base_amount = 20
    amount = int(base_amount * phase_info.energy_multiplier)

    acc.balance += amount
    acc.last_daily_bonus_date = today

    await db.commit()
    await db.refresh(acc)

    return True, acc, amount
