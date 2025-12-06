from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Phnom_Penh")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    habits: Mapped[list["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    plants: Mapped[list["Plant"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    artifacts: Mapped[list["UserArtifact"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    lunar_energy_account: Mapped["LunarEnergyAccount"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
