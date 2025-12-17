from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from .config import settings

MoonPhase = Literal["new", "waxing", "full", "waning"]


@dataclass
class MoonPhaseInfo:
    phase: MoonPhase
    energy_multiplier: float
    theme_id: str


def _julian_date(dt: datetime) -> float:
    """
    Very rough Julian date converter for moon phase calculation.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    year = dt.year
    month = dt.month
    day = dt.day + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    return jd


def _moon_phase_fraction(dt: datetime) -> float:
    """
    Return fraction of the lunar cycle (0.0..1.0), where 0 is new moon.
    Based on a simple approximation (good enough for game logic).
    """
    jd = _julian_date(dt)
    # Reference new moon: 2000-01-06 18:14 UT (approx)
    known_new_moon_jd = 2451550.1
    synodic_month = 29.53058867
    days_since_new = jd - known_new_moon_jd
    return (days_since_new / synodic_month) % 1.0


def get_moon_phase(dt: datetime) -> MoonPhase:
    """
    Map fraction to one of the 4 phases.
    """
    frac = _moon_phase_fraction(dt)
    if frac < 0.125 or frac >= 0.875:
        return "new"
    elif 0.125 <= frac < 0.375:
        return "waxing"
    elif 0.375 <= frac < 0.625:
        return "full"
    else:
        return "waning"


def get_moon_phase_info(dt: datetime) -> MoonPhaseInfo:
    phase = get_moon_phase(dt)
    multiplier = settings.MOON_PHASE_MULTIPLIERS.get(phase, 1.0)
    theme_id = settings.MOON_PHASE_THEME_IDS.get(phase, "night_dim")
    return MoonPhaseInfo(phase=phase, energy_multiplier=multiplier, theme_id=theme_id)
