# FILE: app/services/habit_service.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple

import pytz
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.habit import Habit
from app.models.lunar_energy import LunarEnergyAccount
from app.models.plant import Plant
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitUpdate
from app.services.lunar_service import get_or_create_energy_account, get_today_lunar_phase


def _compute_stage_from_streak(streak: int) -> str:
    if streak >= 22:
        return "radiant"
    if streak >= 15:
        return "blooming"
    if streak >= 8:
        return "flourishing"
    if streak >= 4:
        return "young"
    return "seedling"


def _required_interval_days(habit: Habit) -> int:
    """
    Возвращает требуемый интервал между выполнениями в днях
    в зависимости от частоты привычки.
    """
    value = habit.frequency_value or 1
    if habit.frequency_type == "daily":
        return 1
    if habit.frequency_type == "weekly":
        return 7 * max(1, value)  # обычно 7
    if habit.frequency_type == "custom_days":
        return max(1, value)
    if habit.frequency_type == "custom_weeks":
        return 7 * max(1, value)
    return 1


async def list_habits(db: AsyncSession, user: User) -> list[Habit]:
    stmt = select(Habit).where(Habit.user_id == user.id).order_by(Habit.created_at.asc())
    result = await db.execute(stmt)
    return list(result.scalars())


async def create_habit(db: AsyncSession, user: User, payload: HabitCreate) -> Habit:
    """
    Создание привычки с учётом:
    - initial_days (уже пройденные дни)
    - frequency_type / frequency_value (таймфрейм)
    """
    initial_days = payload.initial_days or 0

    # Приводим частоту к сохранённому виду
    freq_type = payload.frequency_type or "daily"
    freq_value: int

    if freq_type == "daily":
        freq_value = 1
    elif freq_type == "weekly":
        freq_value = 1  # "раз в 1 неделю"
    elif freq_type in ("custom_days", "custom_weeks"):
        if payload.frequency_value is None:
            # По умолчанию раз в 1 (день/неделю)
            freq_value = 1
        else:
            freq_value = max(1, payload.frequency_value)
    else:
        freq_type = "daily"
        freq_value = 1

    habit = Habit(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        cooldown_hours=payload.cooldown_hours,
        initial_days=initial_days,
        frequency_type=freq_type,
        frequency_value=freq_value,
        streak_current=initial_days,
        streak_best=initial_days,
    )
    db.add(habit)
    await db.flush()

    stage = _compute_stage_from_streak(initial_days)
    plant = Plant(
        user_id=user.id,
        habit_id=habit.id,
        species="lotus",
        stage=stage,
        glow_level=min(5, max(1, initial_days // 5 + 1)) if initial_days > 0 else 1,
    )
    db.add(plant)
    await db.flush()

    return habit


async def update_habit(db: AsyncSession, user: User, habit_id: int, payload: HabitUpdate) -> Habit:
    stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id)
    result = await db.execute(stmt)
    habit = result.scalar_one_or_none()
    if not habit:
        raise ValueError("Habit not found")

    if payload.name is not None:
        habit.name = payload.name
    if payload.description is not None:
        habit.description = payload.description
    if payload.is_active is not None:
        habit.is_active = payload.is_active
    if payload.cooldown_hours is not None:
        habit.cooldown_hours = payload.cooldown_hours

    # Обновление частоты (при желании)
    if payload.frequency_type is not None:
        habit.frequency_type = payload.frequency_type
    if payload.frequency_value is not None:
        habit.frequency_value = max(1, payload.frequency_value)

    await db.flush()
    return habit


async def delete_habit(db: AsyncSession, user: User, habit_id: int) -> None:
    stmt = delete(Habit).where(Habit.id == habit_id, Habit.user_id == user.id)
    await db.execute(stmt)


async def get_habit_for_user(db: AsyncSession, user: User, habit_id: int) -> Habit:
    stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id)
    result = await db.execute(stmt)
    habit = result.scalar_one_or_none()
    if not habit:
        raise ValueError("Habit not found")
    return habit


async def ensure_plant_for_habit(db: AsyncSession, habit: Habit) -> Plant:
    if habit.plant:
        return habit.plant
    plant = Plant(
        user_id=habit.user_id,
        habit_id=habit.id,
        species="lotus",
        stage=_compute_stage_from_streak(habit.streak_current),
        glow_level=min(5, max(1, habit.streak_current // 5 + 1)) if habit.streak_current > 0 else 1,
    )
    db.add(plant)
    await db.flush()
    return plant


async def _apply_daily_checkin(
    db: AsyncSession,
    user: User,
    habit: Habit,
    account: LunarEnergyAccount,
    now_utc: datetime | None = None,
) -> Tuple[Habit, Plant, int]:
    """
    Core streak & reward logic.

    С учётом частоты:
      - daily:    раз в 1 день
      - weekly:   раз в 7 дней
      - custom_*: раз в N дней/недель

    Правила:
      - если отметились раньше, чем прошло нужное количество дней → ошибка "рано"
      - если ровно через нужный интервал → стрик +1
      - если сильно позже → стрик с нуля и завядание
    """
    if now_utc is None:
        now_utc = datetime.now(tz=timezone.utc)

    tz = pytz.timezone(user.timezone or settings.DEFAULT_TIMEZONE)
    local_dt = now_utc.astimezone(tz)
    today = local_dt.date()

    # Доп. кулдаун по часам (необязательно использовать)
    if habit.last_completed_at and habit.cooldown_hours > 0:
        delta = now_utc - habit.last_completed_at
        if delta < timedelta(hours=habit.cooldown_hours):
            raise RuntimeError("Habit is on cooldown")

    interval_days = _required_interval_days(habit)

    if habit.last_completed_date == today:
        raise RuntimeError("Habit already completed today")
    elif habit.last_completed_date is None:
        # первый чек-ин в приложении продолжает стрик с initial_days
        habit.streak_current = (habit.streak_current or 0) + 1
    else:
        diff = (today - habit.last_completed_date).days

        if diff < interval_days:
            # Слишком рано для следующей отметки (например, привычка раз в неделю)
            raise RuntimeError("Too early to check in for this habit")
        elif diff == interval_days:
            # В окно — стрик растёт
            habit.streak_current += 1
        elif diff > interval_days:
            # Окно пропущено — стрик обрывается и растение вянет
            habit.streak_current = 1
            habit.is_wilted = True
            habit.last_wilted_at = now_utc

    if habit.streak_current > habit.streak_best:
        habit.streak_best = habit.streak_current

    habit.last_completed_date = today
    habit.last_completed_at = now_utc

    plant = await ensure_plant_for_habit(db, habit)
    new_stage = _compute_stage_from_streak(habit.streak_current)
    plant.stage = new_stage
    plant.is_wilted = habit.is_wilted
    plant.glow_level = min(5, max(1, habit.streak_current // 5 + 1))
    plant.last_evolved_at = now_utc

    phase_info = await get_today_lunar_phase(user, now_utc)
    base_reward = 5
    streak_bonus = min(20, habit.streak_current // 3)
    if habit.is_wilted:
        streak_bonus = streak_bonus // 2

    gained = int((base_reward + streak_bonus) * phase_info.energy_multiplier)
    account.balance += gained

    await db.flush()
    return habit, plant, gained


async def cleanse_habit_with_moonlight(
    db: AsyncSession, user: User, habit: Habit, account: LunarEnergyAccount, cost: int = 25
) -> None:
    if not habit.is_wilted:
        return
    if account.balance < cost:
        raise RuntimeError("Not enough moonlight to cleanse")
    account.balance -= cost
    habit.is_wilted = False
    await db.flush()


async def checkin_habit(
    db: AsyncSession, user: User, habit_id: int, force_cleansing: bool = False
) -> Tuple[Habit, Plant, int]:
    habit = await get_habit_for_user(db, user, habit_id)
    account = await get_or_create_energy_account(db, user)

    if habit.is_wilted and force_cleansing:
        await cleanse_habit_with_moonlight(db, user, habit, account)

    habit, plant, gained = await _apply_daily_checkin(db, user, habit, account)
    return habit, plant, gained
