from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(tz=timezone.utc)
    expire = now + expires_delta

    to_encode: Dict[str, Any] = {"sub": str(subject), "iat": int(now.timestamp()), "exp": int(expire.timestamp())}

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


def _telegram_check_string(data: Dict[str, Any]) -> str:
    data_check_arr = [f"{k}={data[k]}" for k in sorted(data.keys()) if k != "hash"]
    return "\n".join(data_check_arr)


def verify_telegram_webapp_init_data(init_data: Dict[str, Any]) -> bool:
    if "hash" not in init_data:
        return False

    received_hash = init_data["hash"]
    data_copy = {k: v for k, v in init_data.items() if k != "hash"}

    check_string = _telegram_check_string(data_copy)

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received_hash, computed_hash):
        return False

    auth_date = init_data.get("auth_date")
    if auth_date:
        try:
            auth_ts = int(auth_date)
            now_ts = int(time.time())
            if now_ts - auth_ts > 86400:
                return False
        except (ValueError, TypeError):
            return False

    return True
