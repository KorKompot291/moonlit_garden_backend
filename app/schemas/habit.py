# FILE: app/schemas/habit.py
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Типы частоты для API
HabitFrequencyType = Literal["daily", "weekly", "custom_days", "custom_weeks"]


class HabitBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    # уже пройденные до приложения дни
    initial_days: int

    # частота выполнения
    frequency_type: HabitFrequencyType
    frequency_value: int

    streak_current: int
    streak_best: int
    last_completed_date: Optional[date] = None
    last_completed_at: Optional[datetime] = None
    cooldown_hours: int
    is_wilted: bool
    created_at: datetime
    updated_at: datetime


class HabitCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=512)
    cooldown_hours: int = Field(0, ge=0, le=72)

    # Сколько дней человек уже выполняет привычку до приложения
    initial_days: int = Field(
        0,
        ge=0,
        le=3650,
        description="Сколько дней вы уже выполняете эту привычку до начала использования приложения",
    )

    # Выбор таймфрейма:
    # - daily        → каждый день
    # - weekly       → раз в неделю
    # - custom_days  → раз в N дней
    # - custom_weeks → раз в N недель
    frequency_type: HabitFrequencyType = Field(
        "daily",
        description="daily / weekly / custom_days / custom_weeks",
    )

    # Для custom_* обязательно, для daily/weekly можно не заполнять
    frequency_value: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="N для custom_days/custom_weeks (раз в N дней/недель)",
    )


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None
    cooldown_hours: Optional[int] = Field(None, ge=0, le=72)

    # Можно менять частоту (по желанию)
    frequency_type: Optional[HabitFrequencyType] = Field(
        None,
        description="daily / weekly / custom_days / custom_weeks",
    )
    frequency_value: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="N для custom_days/custom_weeks",
    )
    # initial_days здесь не трогаем, чтобы не ломать историю


class HabitCheckinRequest(BaseModel):
    """
    Request body for marking today's completion.

    `force_cleansing` means: if habit is wilted, attempt to spend moonlight to cleanse & continue.
    """

    force_cleansing: bool = False


class HabitCheckinResponse(BaseModel):
    habit: HabitBase
    plant_stage: str
    gained_moonlight: int
    total_moonlight: int
    moon_phase: str
    energy_multiplier: float
