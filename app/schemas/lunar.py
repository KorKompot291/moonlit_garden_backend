from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class LunarPhaseResponse(BaseModel):
    phase: str
    age_days: float
    illumination: float
    energy_multiplier: float
    visual_theme_id: str
    local_date: date
    timezone: str


class LunarEnergyGetResponse(BaseModel):
    balance: int
    last_daily_bonus_date: date | None


class LunarEnergyUseRequest(BaseModel):
    amount: int
    reason: str | None = None


class LunarEnergyUseResponse(BaseModel):
    balance: int
    spent: int
