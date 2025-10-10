from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time

from django.utils import timezone


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


def local_month_bounds(year: int, month: int):
    """Return the start and end datetimes for a month in Antananarivo."""

    _, last_day = monthrange(year, month)
    tz = get_local_timezone()
    start = timezone.make_aware(datetime(year, month, 1, 0, 0, 0), tz)
    end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59), tz)
    return start, end
