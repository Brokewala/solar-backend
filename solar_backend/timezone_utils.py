from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, tzinfo
from typing import List, Optional
from zoneinfo import ZoneInfo

from django.utils import timezone

WeekSlice = dict


def resolve_timezone(tz: Optional[str | tzinfo] = None) -> tzinfo:
    """Resolve a timezone name or object to a tzinfo instance."""

    if tz is None:
        return get_local_timezone()
    if isinstance(tz, tzinfo):
        return tz
    try:
        return ZoneInfo(tz)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Invalid timezone: {tz}") from exc


def get_local_timezone():
    """Return the project's default timezone (Antananarivo)."""

    return timezone.get_default_timezone()


def local_now():
    """Return the current datetime localized in Antananarivo."""

    return timezone.localtime(timezone.now(), get_local_timezone())


def local_today():
    """Return today's date in Antananarivo."""

    return timezone.localdate()


def ensure_local_aware(value: datetime) -> datetime:
    """Ensure a datetime is aware in the Antananarivo timezone."""

    tz = get_local_timezone()
    if timezone.is_naive(value):
        return timezone.make_aware(value, tz)
    return value.astimezone(tz)


def local_day_bounds(target: date | datetime):
    """Return the start and end datetimes for a day in Antananarivo."""

    if isinstance(target, datetime):
        target_date = target.date()
    else:
        target_date = target

    tz = get_local_timezone()
    start = timezone.make_aware(datetime.combine(target_date, time(0, 0, 0)), tz)
    end = timezone.make_aware(datetime.combine(target_date, time(23, 59, 59)), tz)
    return start, end


def local_month_bounds(year: int, month: int, tz: Optional[str | tzinfo] = None):
    """Return the start and end datetimes for a month in the provided timezone."""

    tzinfo = resolve_timezone(tz)
    _, last_day = monthrange(year, month)
    start = timezone.make_aware(datetime(year, month, 1, 0, 0, 0), tzinfo)
    end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59), tzinfo)
    return start, end


def local_week_slices_for_month(
    year: int, month: int, tz: Optional[str | tzinfo] = None
) -> List[WeekSlice]:
    """Return the configured week slices for a month in the provided timezone."""

    resolve_timezone(tz)  # Validate timezone early even if not directly used here.
    _, last_day = monthrange(year, month)
    ranges = [
        (1, min(7, last_day)),
        (8, min(14, last_day)) if last_day >= 8 else None,
        (15, min(21, last_day)) if last_day >= 15 else None,
        (22, min(28, last_day)) if last_day >= 22 else None,
        (29, last_day) if last_day >= 29 else None,
    ]

    week_slices: List[WeekSlice] = []
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


def safe_float(value, default: float = 0.0) -> float:
    """Safely cast a value to float, returning a default on failure."""

    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
