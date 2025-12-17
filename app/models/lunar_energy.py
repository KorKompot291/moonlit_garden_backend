from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class LunarEnergyAccount(Base):
    __tablename__ = "lunarenergyaccount"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)

    balance = Column(Integer, nullable=False, default=0)

    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_daily_bonus_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="lunar_energy_account")
