from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class HabitFrequencyType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM_DAYS = "custom_days"
    CUSTOM_WEEKS = "custom_weeks"


class HabitKind(str, Enum):
    PLANT = "plant"
    MUSHROOM = "mushroom"


class Habit(Base):
    __tablename__ = "habit"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)

    # "I already do this for N days" — we store this as offset on creation
    initial_days_offset = Column(Integer, nullable=False, default=0)

    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)

    last_check_in_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    is_active = Column(Boolean, nullable=False, default=True)

    # frequency logic
    frequency_type = Column(SAEnum(HabitFrequencyType, name="habit_frequency_type_enum"), nullable=False)
    frequency_value = Column(Integer, nullable=True)  # N days or N weeks for custom types

    # plant vs mushroom
    kind = Column(SAEnum(HabitKind, name="habit_kind_enum"), nullable=False, default=HabitKind.PLANT)

    user = relationship("User", back_populates="habits")
    plant = relationship("Plant", back_populates="habit", uselist=False, cascade="all, delete-orphan")
