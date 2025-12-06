# FILE: app/models/habit.py
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Частота выполнения привычки
HABIT_FREQUENCY_TYPE_CHOICES = (
    "daily",         # каждый день
    "weekly",        # раз в неделю
    "custom_days",   # раз в N дней
    "custom_weeks",  # раз в N недель
)


class Habit(Base):
    """
    Habit entity. Each habit is mirrored by a plant in the garden.

    - initial_days: сколько дней человек уже занимался этой привычкой до приложения
    - frequency_type / frequency_value: как часто нужно выполнять привычку
    - streak_current: текущий стрик (учитывает initial_days + дни в приложении)
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 🔹 Сколько дней до начала приложения человек уже делал эту привычку
    initial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 🔹 Частота привычки
    frequency_type: Mapped[str] = mapped_column(
        Enum(*HABIT_FREQUENCY_TYPE_CHOICES, name="habit_frequency_type_enum"),
        nullable=False,
        default="daily",
    )
    # frequency_value:
    # - для daily / weekly обычно 1
    # - для custom_days — "раз в N дней"
    # - для custom_weeks — "раз в N недель"
    frequency_value: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    streak_current: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_best: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Дополнительный "тонкий" кулдаун в часах (можно оставить 0, если не нужен)
    cooldown_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_wilted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_wilted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="habits")
    plant: Mapped["Plant"] = relationship(back_populates="habit", uselist=False, cascade="all, delete-orphan")
