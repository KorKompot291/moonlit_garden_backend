from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PlantOut(BaseModel):
    id: int
    user_id: int
    habit_id: int
    species: str
    is_mushroom: bool
    growth_stage: int
    growth_points: int
    is_wilted: bool
    last_grown_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
