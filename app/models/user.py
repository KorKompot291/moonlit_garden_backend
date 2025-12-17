from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)  
    timezone = Column(String(64), nullable=False, default="UTC")

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    plants = relationship("Plant", back_populates="user", cascade="all, delete-orphan")
    artifacts = relationship("UserArtifact", back_populates="user", cascade="all, delete-orphan")
    lunar_energy_account = relationship(
        "LunarEnergyAccount",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
