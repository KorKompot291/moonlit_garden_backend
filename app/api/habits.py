from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.habit import (
    HabitBase,
    HabitCheckinRequest,
    HabitCheckinResponse,
    HabitCreate,
    HabitUpdate,
)
from app.services.habit_service import (
    checkin_habit,
    create_habit,
    delete_habit,
    list_habits,
    update_habit,
)
from app.services.lunar_service import get_or_create_energy_account, get_today_lunar_phase

router = APIRouter()


@router.get("/", response_model=List[HabitBase], summary="List habits")
async def list_user_habits(db: DBSession, current_user: CurrentUser) -> List[HabitBase]:
    habits = await list_habits(db, current_user)
    return [HabitBase.model_validate(h) for h in habits]


@router.post("/", response_model=HabitBase, status_code=status.HTTP_201_CREATED, summary="Create habit")
async def create_user_habit(
    payload: HabitCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> HabitBase:
    habit = await create_habit(db, current_user, payload)
    await db.commit()
    await db.refresh(habit)
    return HabitBase.model_validate(habit)


@router.patch("/{habit_id}", response_model=HabitBase, summary="Update habit")
async def update_user_habit(
    habit_id: int,
    payload: HabitUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> HabitBase:
    try:
        habit = await update_habit(db, current_user, habit_id, payload)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    await db.commit()
    await db.refresh(habit)
    return HabitBase.model_validate(habit)


@router.delete(
    "/{habit_id}",
    status_code=status.HTTP_200_OK,   # ⬅ был 204, ставим 200
    summary="Delete habit",
)
async def delete_user_habit(
    habit_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> dict:
    await delete_habit(db, current_user, habit_id)
    await db.commit()
    # Возвращаем простой JSON, без тела на 204
    return {"status": "deleted"}


@router.post("/{habit_id}/checkin", response_model=HabitCheckinResponse, summary="Complete today's habit")
async def checkin_user_habit(
    habit_id: int,
    payload: HabitCheckinRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> HabitCheckinResponse:
    try:
        habit, plant, gained = await checkin_habit(db, current_user, habit_id, payload.force_cleansing)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    account = await get_or_create_energy_account(db, current_user)
    phase_info = await get_today_lunar_phase(current_user)

    await db.commit()
    await db.refresh(habit)
    await db.refresh(account)

    return HabitCheckinResponse(
        habit=HabitBase.model_validate(habit),
        plant_stage=plant.stage,
        gained_moonlight=gained,
        total_moonlight=account.balance,
        moon_phase=phase_info.phase,
        energy_multiplier=phase_info.energy_multiplier,
    )
