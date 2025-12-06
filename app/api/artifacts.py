from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.artifact import (
    ArtifactDefinitionBase,
    ArtifactDiscoverResponse,
    ArtifactListResponse,
    ArtifactWithDefinition,
)
from app.services.artifact_service import discover_artifact, list_user_artifacts
from app.services.lunar_service import get_or_create_energy_account, get_today_lunar_phase

router = APIRouter()


@router.get("/list", response_model=ArtifactListResponse, summary="List user artifacts")
async def list_artifacts(db: DBSession, current_user: CurrentUser) -> ArtifactListResponse:
    rows = await list_user_artifacts(db, current_user)
    artifacts: List[ArtifactWithDefinition] = []
    for ua, definition in rows:
        artifacts.append(
            ArtifactWithDefinition(
                artifact=ArtifactDefinitionBase.model_validate(ua),
                definition=ArtifactDefinitionBase.model_validate(definition),
            )
        )
    return ArtifactListResponse(artifacts=artifacts)


@router.post(
    "/discover",
    response_model=ArtifactDiscoverResponse,
    summary="Discover a new artifact using moonlight",
)
async def discover_new_artifact(
    db: DBSession,
    current_user: CurrentUser,
) -> ArtifactDiscoverResponse:
    cost = 50
    account = await get_or_create_energy_account(db, current_user)
    if account.balance < cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough moonlight")

    account.balance -= cost

    phase_info = await get_today_lunar_phase(current_user)
    ua, definition = await discover_artifact(db, current_user, phase_info)

    await db.commit()
    await db.refresh(account)

    awd = ArtifactWithDefinition(
        artifact=ArtifactDefinitionBase.model_validate(ua),
        definition=ArtifactDefinitionBase.model_validate(definition),
    )

    return ArtifactDiscoverResponse(discovered=awd, remaining_moonlight=account.balance)
