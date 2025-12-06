from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

ARTIFACT_RARITY_CHOICES = ("common", "rare", "legendary", "mythic")


class ArtifactDefinition(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    rarity: Mapped[str] = mapped_column(
        Enum(*ARTIFACT_RARITY_CHOICES, name="artifact_rarity_enum"),
        nullable=False,
        default="common",
    )

    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="crystal")

    unlock_condition: Mapped[str] = mapped_column(String(64), nullable=False, default="none")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_artifacts: Mapped[list["UserArtifact"]] = relationship(back_populates="artifact_definition")


class UserArtifact(Base):
    __table_args__ = (
        UniqueConstraint("user_id", "artifact_definition_id", name="uq_user_artifact_unique"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    artifact_definition_id: Mapped[int] = mapped_column(
        ForeignKey("artifactdefinition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_displayed: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="artifacts")
    artifact_definition: Mapped["ArtifactDefinition"] = relationship(back_populates="user_artifacts")
