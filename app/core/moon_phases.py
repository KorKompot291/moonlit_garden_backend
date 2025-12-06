from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from functools import lru_cache
from typing import Literal

import pytz
from math import cos, pi

from app.core.config import settings

MoonPhaseName = Literal["new", "waxing", "full", "waning"]


@dataclass(frozen=True)
class MoonPhaseInfo:
    phase: MoonPhaseName
    age_days: float
    illumination: float
    energy_multiplier: float
    visual_theme_id: str


@lru_cache(maxsize=512)
def _julian_day(y: int, m: int, d: int) -> float:
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5
    return jd


def _moon_age_days(d: date) -> float:
    base = date(2000, 1, 6)
    synodic_month = 29.53058867
    days_since = (_julian_day(d.year, d.month, d.day) - _julian_day(base.year, base.month, base.day))
    age = days_since % synodic_month
    return age


def _phase_from_age(age: float) -> MoonPhaseName:
    if age < 3 or age > 27:
        return "new"
    if 3 <= age < 11:
        return "waxing"
    if 11 <= age < 19:
        return "full"
    return "waning"


def _illumination_from_age(age: float) -> float:
    synodic_month = 29.53058867
    phase = age / synodic_month
    illumination = 0.5 * (1 - cos(2 * pi * phase))
    return max(0.0, min(1.0, illumination))


def get_moon_phase_for_timezone(
    dt: datetime | None = None,
    timezone_name: str | None = None,
) -> MoonPhaseInfo:
    if dt is None:
        dt = datetime.now(tz=timezone.utc)

    tz_name = timezone_name or settings.DEFAULT_TIMEZONE
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone(settings.DEFAULT_TIMEZONE)

    local_dt = dt.astimezone(tz)
    local_date = local_dt.date()

    age = _moon_age_days(local_date)
    phase = _phase_from_age(age)
    illumination = _illumination_from_age(age)

    multiplier = settings.MOON_PHASE_MULTIPLIERS.get(phase, 1.0)
    theme_id = settings.MOON_PHASE_THEME_IDS.get(phase, "night")

    return MoonPhaseInfo(
        phase=phase,
        age_days=age,
        illumination=illumination,
        energy_multiplier=multiplier,
        visual_theme_id=theme_id,
    )
