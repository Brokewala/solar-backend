from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, tzinfo
from typing import List, Optional
from zoneinfo import ZoneInfo

DEFAULT_TZ_NAME = "Indian/Antananarivo"


def get_tz(tz_name: Optional[str]) -> tzinfo:
    """Return a tzinfo instance for the provided timezone name."""

    if not tz_name:
        return ZoneInfo(DEFAULT_TZ_NAME)
    try:
        return ZoneInfo(tz_name)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid timezone: {tz_name}") from exc


def local_month_bounds(year: int, month: int, tz: tzinfo) -> tuple[datetime, datetime]:
    """Return timezone-aware start and end datetimes for the month."""

    _, last_day = monthrange(year, month)
    start = datetime(year, month, 1, 0, 0, 0, tzinfo=tz)
    end = datetime(year, month, last_day, 23, 59, 59, 999999, tzinfo=tz)
    return start, end


def day_bounds(target: date | datetime, tz: tzinfo) -> tuple[datetime, datetime]:
    """Return timezone-aware bounds for the provided day."""

    if isinstance(target, datetime):
        day = target.date()
    else:
        day = target

    start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=tz)
    end = datetime(day.year, day.month, day.day, 23, 59, 59, 999999, tzinfo=tz)
    return start, end


def week_slices_for_month(year: int, month: int, tz: tzinfo) -> List[dict]:
    """Return week slice definitions for the month using fixed day ranges."""

    # Validate timezone early to mirror expectations (tz used for awareness elsewhere)
    if tz is None:
        raise ValueError("Timezone must not be None")

    _, last_day = monthrange(year, month)
    ranges = [
        (1, min(7, last_day)),
        (8, min(14, last_day)) if last_day >= 8 else None,
        (15, min(21, last_day)) if last_day >= 15 else None,
        (22, min(28, last_day)) if last_day >= 22 else None,
        (29, last_day) if last_day >= 29 else None,
    ]

    week_slices: List[dict] = []
    week_index = 1
    for week_range in ranges:
        if not week_range:
            continue
        start_day, end_day = week_range
        start_date = date(year, month, start_day)
        end_date = date(year, month, end_day)
        week_slices.append(
            {
                "week_index": week_index,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
        week_index += 1

    return week_slices


def safe_float(value: Optional[str | float | int], default: float = 0.0) -> float:
    """Safely convert the provided value to a float."""

    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
