from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit, HabitFrequencyType, HabitKind
from app.models.plant import Plant
from app.schemas.habit import HabitCreate, HabitUpdate, HabitCheckInResponse


def _calculate_growth_gain(habit: Habit) -> int:
    """
    How many growth points plant gets per successful check-in.
    Could depend on frequency or kind.
    """
    base = 10
    if habit.kind == HabitKind.MUSHROOM:
        base += 5
    if habit.frequency_type in (HabitFrequencyType.CUSTOM_DAYS, HabitFrequencyType.CUSTOM_WEEKS):
        base += 3
    return base


def _update_growth_stage(plant: Plant) -> None:
    """
    Simple thresholds for growth stages.
    """
    thresholds = [0, 20, 50, 100, 200]
    stage = 0
    for i, t in enumerate(thresholds):
        if plant.growth_points >= t:
            stage = i
    plant.growth_stage = stage


async def create_habit_for_user(
    db: AsyncSession,
    user_id: int,
    habit_in: HabitCreate,
) -> Habit:
    habit = Habit(
        user_id=user_id,
        name=habit_in.name,
        description=habit_in.description,
        initial_days_offset=habit_in.initial_days_offset,
        current_streak=habit_in.initial_days_offset,
        longest_streak=habit_in.initial_days_offset,
        frequency_type=habit_in.frequency_type,
        frequency_value=habit_in.frequency_value,
        kind=habit_in.kind,
    )

    db.add(habit)
    await db.flush()

    # create plant
    plant = Plant(
        user_id=user_id,
        habit_id=habit.id,
        species="mushroom_seed" if habit_in.kind == HabitKind.MUSHROOM else "forest_seed",
        is_mushroom=habit_in.kind == HabitKind.MUSHROOM,
        growth_stage=0,
        growth_points=habit_in.initial_days_offset * 5,
        is_wilted=False,
    )
    _update_growth_stage(plant)
    db.add(plant)

    await db.commit()
    await db.refresh(habit)
    return habit


async def get_user_habits(db: AsyncSession, user_id: int) -> Sequence[Habit]:
    result = await db.execute(select(Habit).where(Habit.user_id == user_id).order_by(Habit.id))
    return result.scalars().all()


async def get_habit_by_id(db: AsyncSession, user_id: int, habit_id: int) -> Habit | None:
    result = await db.execute(
        select(Habit).where(Habit.user_id == user_id, Habit.id == habit_id)
    )
    return result.scalar_one_or_none()


async def update_habit(
    db: AsyncSession,
    habit: Habit,
    data: HabitUpdate,
) -> Habit:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    await db.commit()
    await db.refresh(habit)
    return habit


async def delete_habit(db: AsyncSession, habit: Habit) -> None:
    await db.delete(habit)
    await db.commit()


def _is_expected_checkin_today(habit: Habit, today: date) -> bool:
    """
    Rough check if today is one of allowed days.
    For DAILY: always.
    For WEEKLY: any day, but streak breaks if last_check_in_date < today - 7.
    For CUSTOM: use frequency_value.
    """
    if habit.frequency_type == HabitFrequencyType.DAILY:
        return True

    if habit.last_check_in_date is None:
        return True

    delta_days = (today - habit.last_check_in_date).days
    if habit.frequency_type == HabitFrequencyType.WEEKLY:
        return delta_days >= 1  # can check once per day, but break if too late
    elif habit.frequency_type == HabitFrequencyType.CUSTOM_DAYS:
        return delta_days >= habit.frequency_value
    elif habit.frequency_type == HabitFrequencyType.CUSTOM_WEEKS:
        return delta_days >= (habit.frequency_value or 1) * 7

    return True


async def check_in_habit(
    db: AsyncSession,
    habit: Habit,
    today: date,
) -> HabitCheckInResponse:
    """
    Daily check-in logic: update streak + plant growth.
    """
    # find plant
    result = await db.execute(
        select(Plant).where(Plant.habit_id == habit.id).limit(1)
    )
    plant = result.scalar_one_or_none()
    if not plant:
        plant = Plant(
            user_id=habit.user_id,
            habit_id=habit.id,
            species="forest_seed",
            is_mushroom=habit.kind == HabitKind.MUSHROOM,
        )
        db.add(plant)

    if habit.last_check_in_date is not None:
        delta_days = (today - habit.last_check_in_date).days
        # if missed more than allowed interval -> streak reset & plant wilts
        if delta_days > 1 and habit.frequency_type == HabitFrequencyType.DAILY:
            habit.current_streak = 0
            plant.is_wilted = True
        elif habit.frequency_type == HabitFrequencyType.WEEKLY and delta_days > 7:
            habit.current_streak = 0
            plant.is_wilted = True
        elif habit.frequency_type == HabitFrequencyType.CUSTOM_DAYS and habit.frequency_value:
            if delta_days > habit.frequency_value:
                habit.current_streak = 0
                plant.is_wilted = True
        elif habit.frequency_type == HabitFrequencyType.CUSTOM_WEEKS and habit.frequency_value:
            if delta_days > habit.frequency_value * 7:
                habit.current_streak = 0
                plant.is_wilted = True

    if not _is_expected_checkin_today(habit, today):
        # still allow check-in, but treat like "late" case; we won't reset again here
        pass

    # apply successful check-in
    habit.current_streak += 1
    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak

    habit.last_check_in_date = today
    plant.is_wilted = False

    gain = _calculate_growth_gain(habit)
    plant.growth_points += gain
    _update_growth_stage(plant)

    await db.commit()
    await db.refresh(habit)
    await db.refresh(plant)

    return HabitCheckInResponse(
        habit_id=habit.id,
        current_streak=habit.current_streak,
        longest_streak=habit.longest_streak,
        plant_growth_stage=plant.growth_stage,
        plant_growth_points=plant.growth_points,
        is_wilted=plant.is_wilted,
    )
