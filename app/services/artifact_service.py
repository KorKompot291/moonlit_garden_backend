from __future__ import annotations

import random
from typing import Iterable, List, Tuple

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.moon_phases import MoonPhaseInfo
from app.models.artifact import ARTIFACT_RARITY_CHOICES, ArtifactDefinition, UserArtifact
from app.models.user import User


def _rarity_weights_for_phase(phase: str) -> dict[str, float]:
    base = {
        "common": 70.0,
        "rare": 25.0,
        "legendary": 4.0,
        "mythic": 1.0,
    }
    if phase == "full":
        base["rare"] *= 1.4
        base["legendary"] *= 2.0
        base["mythic"] *= 2.5
        base["common"] *= 0.7
    elif phase == "new":
        base["common"] *= 1.2
        base["rare"] *= 0.9
        base["legendary"] *= 0.7
        base["mythic"] *= 0.5
    elif phase == "waxing":
        base["rare"] *= 1.2
        base["legendary"] *= 1.1
    elif phase == "waning":
        base["rare"] *= 0.9
        base["legendary"] *= 0.9
    return base


def _filter_by_unlock_condition(
    defs: Iterable[ArtifactDefinition], user: User, phase_info: MoonPhaseInfo
) -> list[ArtifactDefinition]:
    filtered: list[ArtifactDefinition] = []
    for d in defs:
        cond = d.unlock_condition or "none"
        if cond == "none":
            filtered.append(d)
        elif cond == "full_moon_only" and phase_info.phase == "full":
            filtered.append(d)
        elif cond == "waxing_only" and phase_info.phase == "waxing":
            filtered.append(d)
        elif cond == "new_moon_only" and phase_info.phase == "new":
            filtered.append(d)
        elif cond == "waning_only" and phase_info.phase == "waning":
            filtered.append(d)
    return filtered


def _weighted_choice(defs: list[ArtifactDefinition], weights: dict[str, float]) -> ArtifactDefinition:
    population = defs
    w = [weights.get(d.rarity, 1.0) for d in defs]
    total = sum(w)
    if not population or total <= 0:
        return random.choice(defs)
    r = random.uniform(0, total)
    cum = 0.0
    for d, weight in zip(population, w):
        cum += weight
        if r <= cum:
            return d
    return population[-1]


async def list_user_artifacts(db: AsyncSession, user: User) -> list[Tuple[UserArtifact, ArtifactDefinition]]:
    stmt: Select = (
        select(UserArtifact, ArtifactDefinition)
        .join(ArtifactDefinition, UserArtifact.artifact_definition_id == ArtifactDefinition.id)
        .where(UserArtifact.user_id == user.id)
        .order_by(UserArtifact.acquired_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [(row[0], row[1]) for row in rows]


async def discover_artifact(
    db: AsyncSession, user: User, phase_info: MoonPhaseInfo
) -> Tuple[UserArtifact, ArtifactDefinition]:
    defs_result = await db.execute(select(ArtifactDefinition))
    all_defs: List[ArtifactDefinition] = list(defs_result.scalars())
    if not all_defs:
        raise RuntimeError("No artifact definitions are configured")

    owned_stmt = select(UserArtifact.artifact_definition_id).where(UserArtifact.user_id == user.id)
    owned_result = await db.execute(owned_stmt)
    owned_ids = {row[0] for row in owned_result.all()}

    available = [d for d in all_defs if d.id not in owned_ids] or all_defs

    available = _filter_by_unlock_condition(available, user, phase_info) or available

    weights = _rarity_weights_for_phase(phase_info.phase)
    chosen_def = _weighted_choice(available, weights)

    ua = UserArtifact(user_id=user.id, artifact_definition_id=chosen_def.id)
    db.add(ua)
    await db.flush()
    return ua, chosen_def
