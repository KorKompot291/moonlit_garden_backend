from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.habit import HabitFrequencyType, HabitKind


class HabitBase(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = None

    initial_days_offset: int = Field(
        0,
        ge=0,
        description="Сколько дней я уже выполняю привычку на момент создания.",
    )

    frequency_type: HabitFrequencyType
    frequency_value: Optional[int] = Field(
        None,
        ge=1,
        description="N для custom_days/custom_weeks (каждые N дней/недель).",
    )

    kind: HabitKind = HabitKind.PLANT


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    initial_days_offset: Optional[int] = Field(None, ge=0)
    frequency_type: Optional[HabitFrequencyType] = None
    frequency_value: Optional[int] = Field(None, ge=1)
    kind: Optional[HabitKind] = None
    is_active: Optional[bool] = None


class HabitOut(HabitBase):
    id: int
    user_id: int
    current_streak: int
    longest_streak: int
    last_check_in_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HabitCheckInResponse(BaseModel):
    habit_id: int
    current_streak: int
    longest_streak: int
    plant_growth_stage: int
    plant_growth_points: int
    is_wilted: bool
