from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel

MoonPhase = Literal["new", "waxing", "full", "waning"]


class LunarPhaseOut(BaseModel):
    phase: MoonPhase
    energy_multiplier: float
    theme_id: str


class LunarEnergyOut(BaseModel):
    balance: int
    last_daily_bonus_date: Optional[date]


class LunarEnergyUseRequest(BaseModel):
    amount: int
    reason: str
