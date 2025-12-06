from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class ArtifactDefinitionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    rarity: str
    kind: str
    unlock_condition: str


class UserArtifactBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    artifact_definition_id: int
    acquired_at: datetime
    is_favorite: bool
    is_displayed: bool


class ArtifactWithDefinition(BaseModel):
    artifact: UserArtifactBase
    definition: ArtifactDefinitionBase


class ArtifactListResponse(BaseModel):
    artifacts: List[ArtifactWithDefinition]


class ArtifactDiscoverResponse(BaseModel):
    discovered: ArtifactWithDefinition
    remaining_moonlight: int
