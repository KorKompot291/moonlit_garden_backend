from __future__ import annotations

from typing import List

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit
from app.models.plant import Plant
from app.models.user import User
from app.schemas.plant import GardenPlant


async def get_garden_state(db: AsyncSession, user: User) -> List[GardenPlant]:
    stmt: Select = (
        select(Plant, Habit)
        .join(Habit, Plant.habit_id == Habit.id)
        .where(Plant.user_id == user.id, Habit.is_active.is_(True))
        .order_by(Habit.created_at.asc())
    )
    result = await db.execute(stmt)
    items: list[GardenPlant] = []
    for plant, habit in result.all():
        items.append(
            GardenPlant(
                id=plant.id,
                habit_id=habit.id,
                habit_name=habit.name,
                species=plant.species,
                stage=plant.stage,
                is_wilted=plant.is_wilted,
                glow_level=plant.glow_level,
                streak_current=habit.streak_current,
                streak_best=habit.streak_best,
            )
        )
    return items
