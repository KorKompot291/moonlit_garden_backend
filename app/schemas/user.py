from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str
    created_at: datetime
    updated_at: datetime


class UserMe(UserBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TelegramWebAppInitRequest(BaseModel):
    init_data: dict


class TelegramAuthResponse(BaseModel):
    token: Token
    user: UserMe
