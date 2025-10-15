"""Shared helpers for the daily data endpoints."""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    FloatField,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Cast, Coalesce

from solar_backend.utils_tz import INDIAN_ANTANARIVO, format_hour_label


def _clean_numeric(value: Any) -> float | None:
    """Attempt to cast a value to float, returning ``None`` on failure."""

    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_daily_points(model, fk_name: str, obj, field: str, start, end):
    """Return ordered raw data points and aggregated totals for a day."""

    tz = ZoneInfo(INDIAN_ANTANARIVO)
    filters = {
        fk_name: obj,
        "createdAt__gte": start,
        "createdAt__lte": end,
    }

    queryset = (
        model.objects.filter(**filters)
        .only("createdAt", field)
        .order_by("createdAt")
    )

    clean_value = Case(
        When(**{f"{field}__isnull": True}, then=Value(None)),
        When(**{f"{field}__exact": ""}, then=Value(None)),
        default=F(field),
        output_field=CharField(),
    )
    numeric_expr = Cast(clean_value, FloatField())
    aggregates = queryset.aggregate(
        total=Coalesce(Sum(numeric_expr), Value(0.0)),
        numeric_count=Count(numeric_expr),
    )

    data = []
    for created_at, raw_value in queryset.values_list("createdAt", field):
        local_dt = created_at.astimezone(tz)
        value = _clean_numeric(raw_value)
        entry = {
            "timestamp": local_dt.isoformat(),
            "hour_label": format_hour_label(local_dt),
            field: value,
        }
        data.append(entry)

    total = float(aggregates.get("total", 0.0) or 0.0)
    numeric_count = int(aggregates.get("numeric_count") or 0)

    return data, {"total": total, "count": numeric_count}


def group_points_by_step(
    data: Iterable[dict[str, Any]], field: str, step_minutes: int
) -> list[dict[str, Any]]:
    """Aggregate points using the provided minute step via averaging."""

    buckets: "OrderedDict[datetime, list[float | None]]" = OrderedDict()
    tz = ZoneInfo(INDIAN_ANTANARIVO)

    for entry in data:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        local_ts = timestamp.astimezone(tz)
        floored_minute = (local_ts.minute // step_minutes) * step_minutes
        bucket_key = local_ts.replace(minute=floored_minute, second=0, microsecond=0)
        buckets.setdefault(bucket_key, []).append(entry.get(field))

    grouped: list[dict[str, Any]] = []
    for dt, values in buckets.items():
        numeric_values = [v for v in values if v is not None]
        averaged_value = (
            sum(numeric_values) / len(numeric_values) if numeric_values else None
        )
        grouped.append(
            {
                "timestamp": dt.isoformat(),
                "hour_label": format_hour_label(dt),
                field: averaged_value,
            }
        )

    grouped.sort(key=lambda item: item["timestamp"])
    return grouped

