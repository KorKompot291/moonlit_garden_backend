from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ArtifactRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ArtifactDefinition(Base):
    """
    Master table for artifacts / achievements.
    """

    __tablename__ = "artifactdefinition"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)

    rarity = Column(SAEnum(ArtifactRarity, name="artifact_rarity_enum"), nullable=False)

    # Optional: some artifacts can be tied to moon phase preferences
    preferred_phase = Column(String(16), nullable=True)  # "new", "full", etc.

    user_artifacts = relationship("UserArtifact", back_populates="artifact_definition")


class UserArtifact(Base):
    """
    Owned artifacts by user.
    """

    __tablename__ = "userartifact"
    __table_args__ = (UniqueConstraint("user_id", "artifact_definition_id", name="uq_user_artifact_single"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    artifact_definition_id = Column(
        Integer,
        ForeignKey("artifactdefinition.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    acquired_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    is_equipped = Column(Integer, nullable=False, default=False)

    user = relationship("User", back_populates="artifacts")
    artifact_definition = relationship("ArtifactDefinition", back_populates="user_artifacts")
