from __future__ import annotations

import random
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moon_phases import get_moon_phase
from app.models.artifact import ArtifactDefinition, ArtifactRarity, UserArtifact
from app.schemas.artifact import ArtifactDefinitionOut, ArtifactDiscoverResponse


RARITY_BASE_WEIGHTS = {
    ArtifactRarity.COMMON: 70,
    ArtifactRarity.RARE: 25,
    ArtifactRarity.EPIC: 4,
    ArtifactRarity.LEGENDARY: 1,
}


def _get_phase_weight_multiplier(phase: str, artifact: ArtifactDefinition) -> float:
    mul = 1.0
    if artifact.preferred_phase and artifact.preferred_phase == phase:
        mul *= 2.0
    if phase == "full" and artifact.rarity in (ArtifactRarity.EPIC, ArtifactRarity.LEGENDARY):
        mul *= 1.5
    if phase == "new" and artifact.rarity == ArtifactRarity.COMMON:
        mul *= 1.2
    return mul


async def get_user_artifacts(db: AsyncSession, user_id: int) -> Sequence[UserArtifact]:
    result = await db.execute(
        select(UserArtifact).where(UserArtifact.user_id == user_id).order_by(UserArtifact.acquired_at)
    )
    return result.scalars().all()


async def discover_artifact(
    db: AsyncSession,
    user_id: int,
) -> ArtifactDiscoverResponse:
    result = await db.execute(select(ArtifactDefinition))
    all_defs = result.scalars().all()
    if not all_defs:
        return ArtifactDiscoverResponse(
            acquired=False,
            artifact=None,
            reason="No artifacts defined yet.",
        )

    now = datetime.utcnow()
    phase = get_moon_phase(now)

    weights = []
    for d in all_defs:
        base = RARITY_BASE_WEIGHTS.get(d.rarity, 1)
        w = base * _get_phase_weight_multiplier(phase, d)
        weights.append(w)

    chosen = random.choices(all_defs, weights=weights, k=1)[0]

    result = await db.execute(
        select(UserArtifact).where(
            UserArtifact.user_id == user_id,
            UserArtifact.artifact_definition_id == chosen.id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return ArtifactDiscoverResponse(
            acquired=False,
            artifact=ArtifactDefinitionOut.model_validate(chosen),
            reason="Already owned.",
        )

    ua = UserArtifact(user_id=user_id, artifact_definition_id=chosen.id)
    db.add(ua)
    await db.commit()
    await db.refresh(ua)
    await db.refresh(chosen)

    return ArtifactDiscoverResponse(
        acquired=True,
        artifact=ArtifactDefinitionOut.model_validate(chosen),
        reason="New artifact discovered!",
    )
