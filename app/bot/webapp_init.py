from __future__ import annotations

from typing import Dict

from app.core.security import create_access_token
from app.models.user import User


def build_webapp_init_payload(user: User) -> Dict[str, str]:
    token = create_access_token(user.id)
    return {"token": token}
