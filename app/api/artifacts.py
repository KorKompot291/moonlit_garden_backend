from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.artifact import ArtifactDiscoverResponse, UserArtifactOut
from app.services.artifact_service import discover_artifact, get_user_artifacts

router = APIRouter()


def _get_token_from_header(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    return authorization.removeprefix("Bearer ").strip()


@router.get("/list", response_model=list[UserArtifactOut], summary="List user artifacts")
async def list_artifacts(
    db: AsyncSession = Depends(get_db),
#    token: str = Depends(_get_token_from_header),
#    user: User = Depends(get_current_user),
) -> list[UserArtifactOut]:
    items = await get_user_artifacts(db, user.id)
    return [UserArtifactOut.model_validate(i) for i in items]


@router.post("/discover", response_model=ArtifactDiscoverResponse, summary="Discover random artifact")
async def discover_artifact_endpoint(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(_get_token_from_header),
    user: User = Depends(get_current_user),
) -> ArtifactDiscoverResponse:
    return await discover_artifact(db, user.id)
