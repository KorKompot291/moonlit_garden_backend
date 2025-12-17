from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moon_phases import get_moon_phase_info
from app.models.habit import Habit
from app.models.plant import Plant
from app.schemas.plant import PlantOut


async def get_garden_state(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """
    Return full garden state for user:
    - plants
    - phases
    - aggregated stats
    """
    result = await db.execute(select(Plant).where(Plant.user_id == user_id))
    plants = result.scalars().all()

    plant_out: List[PlantOut] = [PlantOut.model_validate(p) for p in plants]

    # active habits count
    result = await db.execute(select(Habit).where(Habit.user_id == user_id, Habit.is_active == True))  # noqa: E712
    active_habits_count = len(result.scalars().all())

    phase_info = get_moon_phase_info(None)

    return {
        "plants": [p.model_dump() for p in plant_out],
        "activeHabits": active_habits_count,
        "moon": {
            "phase": phase_info.phase,
            "themeId": phase_info.theme_id,
            "energyMultiplier": phase_info.energy_multiplier,
        },
    }
