from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Plant(Base):
    """
    Visual representation of a habit in the garden.
    """

    __tablename__ = "plant"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
    habit_id = Column(Integer, ForeignKey("habit.id", ondelete="CASCADE"), unique=True, nullable=False)

    # "species" could be used for variety, e.g. "fern", "crystal_flower", "mushroom_luminous"
    species = Column(String(64), nullable=False, default="seedling")
    is_mushroom = Column(Boolean, nullable=False, default=False)

    # growth logic
    growth_stage = Column(Integer, nullable=False, default=0)  # 0 = seed, 1 = sprout, etc.
    growth_points = Column(Integer, nullable=False, default=0)
    is_wilted = Column(Boolean, nullable=False, default=False)

    last_grown_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="plants")
    habit = relationship("Habit", back_populates="plant")
