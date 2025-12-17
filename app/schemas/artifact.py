from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.artifact import ArtifactRarity


class ArtifactDefinitionOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    rarity: ArtifactRarity
    preferred_phase: Optional[str]

    class Config:
        from_attributes = True


class UserArtifactOut(BaseModel):
    id: int
    artifact_definition: ArtifactDefinitionOut
    acquired_at: datetime
    is_equipped: bool

    class Config:
        from_attributes = True


class ArtifactDiscoverResponse(BaseModel):
    acquired: bool
    artifact: Optional[ArtifactDefinitionOut]
    reason: str
