from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlantBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    species: str
    stage: str
    glow_level: int
    is_wilted: bool
    last_evolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GardenPlant(BaseModel):
    id: int
    habit_id: int
    habit_name: str
    species: str
    stage: str
    is_wilted: bool
    glow_level: int
    streak_current: int
    streak_best: int
