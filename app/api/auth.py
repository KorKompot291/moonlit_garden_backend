from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_telegram_webapp_init_data
from app.models.lunar_energy import LunarEnergyAccount
from app.models.user import User
from app.schemas.user import TelegramAuthResponse, TelegramWebAppInitRequest, Token, UserMe

router = APIRouter()


@router.post("/telegram/webapp-init", response_model=TelegramAuthResponse, summary="Login via Telegram WebApp")
async def telegram_webapp_init(
    payload: TelegramWebAppInitRequest,
    db: AsyncSession = Depends(get_db),
) -> TelegramAuthResponse:
    init_data = payload.init_data

    if not verify_telegram_webapp_init_data(init_data):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram init data")

    user_data = init_data.get("user") or {}
    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Telegram user data")

    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            timezone=settings.DEFAULT_TIMEZONE,
        )
        db.add(user)
        await db.flush()

        account = LunarEnergyAccount(user_id=user.id, balance=0)
        db.add(account)
        await db.flush()

    token_str = create_access_token(subject=user.id)
    token = Token(access_token=token_str)

    user_me = UserMe.model_validate(user)

    return TelegramAuthResponse(token=token, user=user_me)
