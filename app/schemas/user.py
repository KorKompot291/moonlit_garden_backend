from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: str | None = None


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
