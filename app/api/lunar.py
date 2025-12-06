from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.lunar import (
    LunarEnergyGetResponse,
    LunarEnergyUseRequest,
    LunarEnergyUseResponse,
    LunarPhaseResponse,
)
from app.services.lunar_service import (
    get_or_create_energy_account,
    get_today_lunar_phase,
    lunar_phase_to_response,
)

router = APIRouter()


@router.get("/today", response_model=LunarPhaseResponse, summary="Get today's moon phase")
async def get_today_lunar(current_user: CurrentUser) -> LunarPhaseResponse:
    info = await get_today_lunar_phase(current_user)
    return lunar_phase_to_response(info, current_user)


@router.get("/energy/get", response_model=LunarEnergyGetResponse, summary="Get moonlight balance")
async def get_energy(db: DBSession, current_user: CurrentUser) -> LunarEnergyGetResponse:
    account = await get_or_create_energy_account(db, current_user)
    return LunarEnergyGetResponse(
        balance=account.balance,
        last_daily_bonus_date=account.last_daily_bonus_date,
    )


@router.post("/energy/use", response_model=LunarEnergyUseResponse, summary="Spend moonlight")
async def use_energy(
    payload: LunarEnergyUseRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> LunarEnergyUseResponse:
    if payload.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")

    account = await get_or_create_energy_account(db, current_user)
    if account.balance < payload.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough moonlight",
        )

    account.balance -= payload.amount
    await db.commit()
    await db.refresh(account)

    return LunarEnergyUseResponse(balance=account.balance, spent=payload.amount)
