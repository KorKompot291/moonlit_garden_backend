from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

PLANT_STAGE_CHOICES = ("seedling", "young", "flourishing", "blooming", "radiant")
PLANT_SPECIES_CHOICES = ("lotus", "mushroom", "crystal", "fern", "vine")


class Plant(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habit.id", ondelete="CASCADE"), nullable=False, unique=True)

    species: Mapped[str] = mapped_column(String(32), nullable=False, default="lotus")
    stage: Mapped[str] = mapped_column(
        Enum(*PLANT_STAGE_CHOICES, name="plant_stage_enum"),
        nullable=False,
        default="seedling",
    )

    glow_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_wilted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_evolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="plants")
    habit: Mapped["Habit"] = relationship(back_populates="plant")
