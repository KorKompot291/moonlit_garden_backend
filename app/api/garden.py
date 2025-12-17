from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.garden_service import get_garden_state

router = APIRouter()


def _get_token_from_header(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    return authorization.removeprefix("Bearer ").strip()


@router.get("/state", summary="Get current garden state for user")
async def garden_state(
    db: AsyncSession = Depends(get_db),
#    token: str = Depends(_get_token_from_header),
#    user: User = Depends(get_current_user),
):
    return await get_garden_state(db, user.id)
