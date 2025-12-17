from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import get_db
from app.models.user import User


def _get_telegram_secret_key(bot_token: str) -> bytes:
    """
    Secret key to verify Telegram WebApp init data.
    """
    return hashlib.sha256(f"WebAppData{bot_token}".encode()).digest()


def verify_telegram_webapp_init_data(init_data: str) -> Dict[str, Any]:
    """
    Verify Telegram WebApp initData according to Telegram docs.

    init_data: raw query string from Telegram WebApp (window.Telegram.WebApp.initData)
    Returns parsed data dict if valid, or raises HTTPException.
    """
    # Parse name=value pairs
    from urllib.parse import parse_qsl

    data_pairs = dict(parse_qsl(init_data, strict_parsing=True))

    received_hash = data_pairs.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=400, detail="Missing hash in init data")

    # Build data_check_string
    data_check_items = [f"{k}={v}" for k, v in sorted(data_pairs.items())]
    data_check_string = "\n".join(data_check_items)

    secret_key = _get_telegram_secret_key(settings.TELEGRAM_BOT_TOKEN)
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=400, detail="Invalid Telegram init data")

    # If there is `user` JSON inside — parse it
    import json

    if "user" in data_pairs:
        try:
            data_pairs["user"] = json.loads(data_pairs["user"])
        except Exception:
            pass

    return data_pairs


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token for WebApp client.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    if extra:
        to_encode.update(extra)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency: get current user from JWT token (Authorization: Bearer <token>).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user
