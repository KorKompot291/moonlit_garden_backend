from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, verify_telegram_webapp_init_data
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter()


class WebAppInitData(BaseModel):
    init_data: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


@router.post("/telegram/webapp", response_model=TokenResponse, summary="Verify Telegram WebApp and issue JWT")
async def auth_telegram_webapp(
    payload: WebAppInitData,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Accepts `init_data` from Telegram WebApp, verifies it, creates/gets user,
    and returns JWT access token to be used by frontend.
    """
    data: Dict[str, Any] = verify_telegram_webapp_init_data(payload.init_data)
    user_payload = data.get("user")
    if not user_payload:
        raise HTTPException(status_code=400, detail="Missing user in init data")

    telegram_id = user_payload.get("id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Missing Telegram id")

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=user_payload.get("username"),
            first_name=user_payload.get("first_name"),
            last_name=user_payload.get("last_name"),
            timezone="UTC",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token(subject=user.id, extra={"tg_id": user.telegram_id})
    return TokenResponse(
        access_token=token,
        user=UserOut.model_validate(user),
    )
