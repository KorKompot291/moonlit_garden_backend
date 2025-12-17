from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Header, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitOut, HabitUpdate, HabitCheckInResponse
from app.services.habit_service import (
    check_in_habit,
    create_habit_for_user,
    delete_habit,
    get_habit_by_id,
    get_user_habits,
    update_habit,
)

router = APIRouter()


def _get_token_from_header(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    return authorization.removeprefix("Bearer ").strip()


@router.get("/", response_model=list[HabitOut], summary="List user habits")
async def list_habits(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> list[HabitOut]:
    habits = await get_user_habits(db, user.id)
    return [HabitOut.model_validate(h) for h in habits]


@router.post("/", response_model=HabitOut, status_code=status.HTTP_201_CREATED, summary="Create habit")
async def create_habit(
    habit_in: HabitCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> HabitOut:
    habit = await create_habit_for_user(db, user.id, habit_in)
    return HabitOut.model_validate(habit)


@router.put("/{habit_id}", response_model=HabitOut, summary="Update habit")
async def update_habit_endpoint(
    habit_id: int,
    habit_in: HabitUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> HabitOut:
    habit = await get_habit_by_id(db, user.id, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit = await update_habit(db, habit, habit_in)
    return HabitOut.model_validate(habit)


@router.delete("/{habit_id}", response_class=Response, summary="Delete habit")
async def delete_habit_endpoint(
    habit_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> Response:
    habit = await get_habit_by_id(db, user.id, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    await delete_habit(db, habit)
    # 204: no content
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{habit_id}/checkin", response_model=HabitCheckInResponse, summary="Daily check-in")
async def checkin_habit_endpoint(
    habit_id: int,
    db: AsyncSession = Depends(get_db),
#  token: str = Depends(_get_token_from_header),
#    user: User = Depends(get_current_user),
) -> HabitCheckInResponse:
    habit = await get_habit_by_id(db, user.id, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    today = date.today()
    result = await check_in_habit(db, habit, today)
    return result
