"""Timezone utilities for daily aggregation endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


INDIAN_ANTANARIVO = "Indian/Antananarivo"


def local_day_bounds(
    year: int, month: int, day: int, tz: str = INDIAN_ANTANARIVO
) -> tuple[datetime, datetime]:
    """Return the inclusive datetime bounds for a day in the given timezone."""

    zone = ZoneInfo(tz)
    start = datetime(year, month, day, tzinfo=zone)
    # Inclusive end of day (23:59:59.999999) for filtering with ``lte``
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start, end


def format_hour_label(dt: datetime, tz: str = INDIAN_ANTANARIVO) -> str:
    """Format a datetime to ``HH:MM`` in the configured timezone."""

    zone = ZoneInfo(tz)
    local_dt = dt.astimezone(zone)
    return local_dt.strftime("%H:%M")

