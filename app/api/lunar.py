from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.moon_phases import get_moon_phase_info
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.lunar import LunarEnergyOut, LunarEnergyUseRequest, LunarPhaseOut
from app.services.lunar_service import (
    apply_daily_bonus,
    apply_lunar_energy_change,
    get_lunar_energy,
)

router = APIRouter()


def _get_token_from_header(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    return authorization.removeprefix("Bearer ").strip()


@router.get("/today", response_model=LunarPhaseOut, summary="Get today's moon phase and theme")
async def get_today_phase() -> LunarPhaseOut:
    now = datetime.utcnow()
    info = get_moon_phase_info(now)
    return LunarPhaseOut(
        phase=info.phase,
        energy_multiplier=info.energy_multiplier,
        theme_id=info.theme_id,
    )


@router.get("/energy/get", response_model=LunarEnergyOut, summary="Get user lunar energy balance")
async def get_energy(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> LunarEnergyOut:
    return await get_lunar_energy(db, user.id)


@router.post("/energy/use", response_model=LunarEnergyOut, summary="Use lunar energy")
async def use_energy(
    payload: LunarEnergyUseRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> LunarEnergyOut:
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    # we simply subtract; if insufficient — error
    current = await get_lunar_energy(db, user.id)
    if current.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Not enough lunar energy")

    acc = await apply_lunar_energy_change(db, user.id, -payload.amount)
    return LunarEnergyOut(balance=acc.balance, last_daily_bonus_date=acc.last_daily_bonus_date)


@router.post("/energy/daily_bonus", response_model=LunarEnergyOut, summary="Claim daily moonlight bonus")
async def claim_daily_bonus(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> LunarEnergyOut:
    today = date.today()
    applied, acc, _amount = await apply_daily_bonus(db, user.id, today)
    if not applied:
        # просто возвращаем текущий баланс
        return LunarEnergyOut(balance=acc.balance, last_daily_bonus_date=acc.last_daily_bonus_date)
    return LunarEnergyOut(balance=acc.balance, last_daily_bonus_date=acc.last_daily_bonus_date)
