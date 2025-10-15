"""Helpers for building weekly aggregates split by month buckets."""
from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

__all__ = ["WeekDefinition", "month_weeks", "week_label_days", "week_index_for_day"]


@dataclass(frozen=True)
class WeekDefinition:
    """Definition of a week bucket within a month."""

    week: int
    start: date
    end: date

    @property
    def day_range(self) -> range:
        """Return the inclusive range of day numbers covered by the bucket."""

        return range(self.start.day, self.end.day + 1)


def month_weeks(year: int, month: int) -> List[WeekDefinition]:
    """Return the configured week buckets for a month.

    Weeks are sliced into the following buckets: [1-7], [8-14], [15-21], [22-28],
    [29-last_day]. The fifth bucket is only returned when the month contains days
    beyond the 28th.
    """

    _, last_day = monthrange(year, month)
    starts = (1, 8, 15, 22, 29)
    weeks: List[WeekDefinition] = []

    for index, start_day in enumerate(starts, start=1):
        if start_day > last_day:
            break
        end_day = min(start_day + 6, last_day)
        weeks.append(
            WeekDefinition(
                week=index,
                start=date(year, month, start_day),
                end=date(year, month, end_day),
            )
        )

    return weeks


def week_label_days() -> List[str]:
    """Return the labels for the days of the week (Monday to Sunday)."""

    return ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]


def week_index_for_day(day: int, weeks: Iterable[WeekDefinition]) -> int | None:
    """Return the index of the week bucket for the given day of month.

    Parameters
    ----------
    day:
        The day of the month (1-based).
    weeks:
        Iterable of week definitions to inspect.

    Returns
    -------
    int | None
        The zero-based index of the bucket containing the day, or ``None`` if no
        bucket matches.
    """

    for idx, definition in enumerate(weeks):
        if day in definition.day_range:
            return idx
    return None
