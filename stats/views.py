from __future__ import annotations




from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError



from solar_backend.utils_daily import fetch_daily_points, group_points_by_step
from solar_backend.utils_tz import INDIAN_ANTANARIVO, local_day_bounds


from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List
from zoneinfo import ZoneInfo

from django.db.models import F, Sum, Value
from django.db.models import FloatField
from django.db.models.functions import Cast, Coalesce, TruncDay, TruncDate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from battery.models import Battery, BatteryData
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData
from solar_backend.timezone_utils import (
    local_month_bounds,
    local_week_slices_for_month,
    resolve_timezone,
)
from .utils import (
    get_tz as stats_get_tz,
    local_month_bounds as stats_local_month_bounds,
    week_slices_for_month as stats_week_slices_for_month,
    day_bounds as stats_day_bounds,
    safe_float as stats_safe_float,
)
from .serializers import WeeklyByMonthResponseSerializer
from .utils_weekly import month_weeks, week_index_for_day, week_label_days


WEEKDAY_LABELS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
ENTITY_ORDER = {"panneau": 0, "batterie": 1, "prise": 2}
PRISE_METRIC_FIELDS = {
    "tension": "tension",
    "puissance": "puissance",
    "courant": "courant",
    "consomation": "consomation",
}
BATTERY_METRIC_FIELDS = {
    "tension": "tension",
    "puissance": "puissance",
    "courant": "courant",
    "energy": "energy",
    "pourcentage": "pourcentage",
}


@dataclass
class EntityConfig:
    name: str
    data_model: type
    module_lookup: str
    metric_fields: Dict[str, str]
    existence_model: type


ENTITY_CONFIGS: Dict[str, EntityConfig] = {
    "panneau": EntityConfig(
        name="panneau",
        data_model=PanneauData,
        module_lookup="panneau__module_id",
        metric_fields={
            "production": "production",
            "tension": "tension",
            "puissance": "puissance",
            "courant": "courant",
        },
        existence_model=Panneau,
    ),
    "batterie": EntityConfig(
        name="batterie",
        data_model=BatteryData,
        module_lookup="battery__module_id",
        metric_fields={
            "tension": "tension",
            "puissance": "puissance",
            "courant": "courant",
            "consommation": "energy",
            "charge": "pourcentage",
        },
        existence_model=Battery,
    ),
    "prise": EntityConfig(
        name="prise",
        data_model=PriseData,
        module_lookup="prise__module_id",
        metric_fields={
            "tension": "tension",
            "puissance": "puissance",
            "courant": "courant",
            "consommation": "consomation",
        },
        existence_model=Prise,
    ),
}


def _daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _available_entities(module_id: str) -> List[str]:
    available: List[str] = []
    for entity_name, config in ENTITY_CONFIGS.items():
        if config.existence_model.objects.filter(module_id=module_id).exists():
            available.append(entity_name)
    return available


def _daily_totals_for_entity(
    config: EntityConfig,
    module_id: str,
    metric_field: str,
    start_of_month,
    end_of_month,
    tzinfo,
) -> Dict[date, float]:
    filters = {config.module_lookup: module_id}

    queryset = (
        config.data_model.objects.filter(
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
            **filters,
        )
        .annotate(local_day=TruncDay("createdAt", tzinfo=tzinfo))
        .values("local_day")
        .annotate(
            total=Coalesce(
                Sum(Cast(F(metric_field), FloatField())),
                Value(0.0),
            )
        )
    )

    totals: Dict[date, float] = {}
    for entry in queryset:
        local_day = entry.get("local_day")
        if local_day is None:
            continue
        day_key = local_day.date() if hasattr(local_day, "date") else local_day
        totals[day_key] = stats_safe_float(entry.get("total"))
    return totals


@api_view(["GET"])
def month_aggregate_view(request, module_id: str, year: int, month: int):
    if month < 1 or month > 12:
        return Response(
            {"detail": "Le mois doit être compris entre 1 et 12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = request.query_params.get("metric")
    if not metric:
        return Response(
            {"detail": "Le paramètre 'metric' est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    metric = metric.lower()

    tz_param = request.query_params.get("tz")
    try:
        tzinfo = resolve_timezone(tz_param)
    except ValueError:
        return Response(
            {"detail": "Le paramètre 'tz' est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    entities_param = request.query_params.get("entities")
    if entities_param:
        requested_entities = [e.strip().lower() for e in entities_param.split(",") if e.strip()]
    else:
        requested_entities = _available_entities(module_id)
        if not requested_entities:
            requested_entities = list(ENTITY_CONFIGS.keys())

    invalid_entities = [e for e in requested_entities if e not in ENTITY_CONFIGS]
    if invalid_entities:
        return Response(
            {"detail": f"Entités inconnues: {', '.join(invalid_entities)}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    deduped_entities: List[str] = []
    seen_entities = set()
    for entity in requested_entities:
        if entity in seen_entities:
            continue
        seen_entities.add(entity)
        deduped_entities.append(entity)

    requested_configs = [ENTITY_CONFIGS[e] for e in deduped_entities]

    for config in requested_configs:
        if metric not in config.metric_fields:
            return Response(
                {
                    "detail": (
                        f"La métrique '{metric}' n'est pas disponible pour l'entité '{config.name}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        start_of_month, end_of_month = local_month_bounds(year, month, tzinfo)
    except ValueError:
        return Response(
            {"detail": "Le fuseau horaire fourni est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    week_slices = local_week_slices_for_month(year, month, tzinfo)

    response_payload = []
    for config in requested_configs:
        metric_field = config.metric_fields[metric]
        daily_totals = _daily_totals_for_entity(
            config,
            module_id,
            metric_field,
            start_of_month,
            end_of_month,
            tzinfo,
        )

        for week in week_slices:
            week_data = [0.0] * 7
            for current_day in _daterange(week["start_date"], week["end_date"]):
                week_data[current_day.weekday()] = daily_totals.get(current_day, 0.0)

            response_payload.append(
                {
                    "week_index": week["week_index"],
                    "range": {
                        "start": week["start_date"].isoformat(),
                        "end": week["end_date"].isoformat(),
                    },
                    "labels": WEEKDAY_LABELS,
                    "data": week_data,
                    "metric": metric,
                    "entity": config.name,
                }
            )

    response_payload.sort(
        key=lambda item: (
            item["week_index"],
            ENTITY_ORDER.get(item["entity"], len(ENTITY_ORDER)),
        )
    )

    return Response(response_payload)


@api_view(["GET"])
def get_prise_monthly_stats(request, module_id: str, year: int, month: int):
    if year < 1970:
        return Response(
            {"detail": "L'année doit être supérieure ou égale à 1970."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if month < 1 or month > 12:
        return Response(
            {"detail": "Le mois doit être compris entre 1 et 12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = request.query_params.get("metric")
    if not metric:
        return Response(
            {"detail": "Le paramètre 'metric' est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = metric.lower()
    if metric not in PRISE_METRIC_FIELDS:
        return Response(
            {
                "detail": (
                    "La métrique doit être l'une des suivantes : "
                    "tension, puissance, courant ou consomation."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    tz_param = request.query_params.get("tz")
    try:
        tzinfo = stats_get_tz(tz_param)
    except ValueError:
        return Response(
            {"detail": "Le paramètre 'tz' est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        stats_local_month_bounds(year, month, tzinfo)
        week_slices = stats_week_slices_for_month(year, month, tzinfo)
    except ValueError:
        return Response(
            {"detail": "L'année ou le mois fourni est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric_field = PRISE_METRIC_FIELDS[metric]

    response_payload = []
    for week in week_slices:
        week_data = [0.0] * 7
        for current_day in _daterange(week["start_date"], week["end_date"]):
            day_start, day_end = stats_day_bounds(current_day, tzinfo)
            total = (
                PriseData.objects.filter(
                    prise__module_id=module_id,
                    createdAt__gte=day_start,
                    createdAt__lte=day_end,
                )
                .aggregate(s=Sum(Cast(F(metric_field), FloatField())))
                .get("s")
            )
            week_data[current_day.weekday()] = stats_safe_float(total)

        response_payload.append(
            {
                "week_index": week["week_index"],
                "range": {
                    "start": week["start_date"].isoformat(),
                    "end": week["end_date"].isoformat(),
                },
                "labels": WEEKDAY_LABELS,
                "data": week_data,
                "metric": metric,
                "entity": "prise",
            }
        )

    response_payload.sort(key=lambda item: item["week_index"])

    return Response(response_payload)


@api_view(["GET"])
def get_panneau_monthly_stats(request, module_id: str, year: int, month: int):
    if year <= 1970:
        return Response(
            {"detail": "L'année doit être supérieure à 1970."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if month < 1 or month > 12:
        return Response(
            {"detail": "Le mois doit être compris entre 1 et 12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = request.query_params.get("metric")
    if not metric:
        return Response(
            {"detail": "Le paramètre 'metric' est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = metric.lower()
    allowed_metrics = {"tension", "puissance", "courant", "production"}
    if metric not in allowed_metrics:
        return Response(
            {
                "detail": (
                    "La métrique doit être l'une des suivantes : "
                    "tension, puissance, courant ou production."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    tz_param = request.query_params.get("tz")
    try:
        tzinfo = stats_get_tz(tz_param)
    except ValueError:
        return Response(
            {"detail": "Le paramètre 'tz' est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        start_of_month, end_of_month = stats_local_month_bounds(year, month, tzinfo)
        week_slices = stats_week_slices_for_month(year, month, tzinfo)
    except ValueError:
        return Response(
            {"detail": "L'année ou le mois fourni est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    monthly_queryset = (
        PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(local_day=TruncDay("createdAt", tzinfo=tzinfo))
        .values("local_day")
        .annotate(
            total=Coalesce(
                Sum(Cast(F(metric), FloatField())),
                Value(0.0, output_field=FloatField()),
            )
        )
    )

    daily_totals: Dict[date, float] = {}
    for row in monthly_queryset:
        local_day = row.get("local_day")
        if local_day is None:
            continue
        day_key = local_day.date() if hasattr(local_day, "date") else local_day
        daily_totals[day_key] = stats_safe_float(row.get("total"))

    response_payload = []
    for week in week_slices:
        week_data = [0.0] * 7
        for current_day in _daterange(week["start_date"], week["end_date"]):
            week_data[current_day.weekday()] = stats_safe_float(
                daily_totals.get(current_day, 0.0)
            )

        response_payload.append(
            {
                "week_index": week["week_index"],
                "range": {
                    "start": week["start_date"].isoformat(),
                    "end": week["end_date"].isoformat(),
                },
                "labels": WEEKDAY_LABELS,
                "data": week_data,
                "metric": metric,
                "entity": "panneau",
            }
        )

    response_payload.sort(key=lambda item: item["week_index"])

    return Response(response_payload)


@api_view(["GET"])
def get_battery_monthly_stats(request, module_id: str, year: int, month: int):
    if year < 1:
        return Response(
            {"detail": "L'année doit être supérieure ou égale à 1."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if month < 1 or month > 12:
        return Response(
            {"detail": "Le mois doit être compris entre 1 et 12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = request.query_params.get("metric")
    if not metric:
        return Response(
            {"detail": "Le paramètre 'metric' est obligatoire."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric = metric.lower()
    if metric not in BATTERY_METRIC_FIELDS:
        return Response(
            {
                "detail": (
                    "La métrique doit être l'une des suivantes : "
                    "tension, puissance, courant, energy ou pourcentage."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    tz_param = request.query_params.get("tz")
    try:
        tzinfo = stats_get_tz(tz_param)
    except ValueError:
        return Response(
            {"detail": "Le paramètre 'tz' est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        start_of_month, end_of_month = stats_local_month_bounds(year, month, tzinfo)
        week_slices = stats_week_slices_for_month(year, month, tzinfo)
    except ValueError:
        return Response(
            {"detail": "L'année ou le mois fourni est invalide."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    metric_field = BATTERY_METRIC_FIELDS[metric]

    monthly_queryset = (
        BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(local_day=TruncDay("createdAt", tzinfo=tzinfo))
        .values("local_day")
        .annotate(
            total=Coalesce(
                Sum(Cast(F(metric_field), FloatField())),
                Value(0.0, output_field=FloatField()),
            )
        )
    )

    daily_totals: Dict[date, float] = {}
    for row in monthly_queryset:
        local_day = row.get("local_day")
        if local_day is None:
            continue
        day_key = local_day.date() if hasattr(local_day, "date") else local_day
        daily_totals[day_key] = stats_safe_float(row.get("total"))

    response_payload = []
    for week in week_slices:
        week_data = [0.0] * 7
        for current_day in _daterange(week["start_date"], week["end_date"]):
            week_data[current_day.weekday()] = stats_safe_float(
                daily_totals.get(current_day, 0.0)
            )

        response_payload.append(
            {
                "week_index": week["week_index"],
                "range": {
                    "start": week["start_date"].isoformat(),
                    "end": week["end_date"].isoformat(),
                },
                "labels": WEEKDAY_LABELS,
                "data": week_data,
                "metric": metric,
                "entity": "battery",
            }
        )

    response_payload.sort(key=lambda item: item["week_index"])

    return Response(response_payload)


class WeeklyByMonthBaseView(APIView):
    """Base view implementing the shared weekly-by-month aggregation logic."""

    entity_name: str = ""
    data_model = None
    module_lookup: str = ""
    allowed_fields: Dict[str, str] = {}
    default_field: str = ""
    timezone_name: str = "Indian/Antananarivo"

    def get(self, request, module_id: str, year: int, month: int):
        if year < 1:
            return Response(
                {"detail": "L'année doit être supérieure ou égale à 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if month < 1 or month > 12:
            return Response(
                {"detail": "Le mois doit être compris entre 1 et 12."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.data_model or not self.module_lookup:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        requested_field = request.query_params.get("field")
        if not requested_field:
            requested_field = self.default_field

        requested_field = requested_field.lower()
        if requested_field not in self.allowed_fields:
            return Response(
                {
                    "detail": (
                        "Le paramètre 'field' doit être l'une des valeurs suivantes : "
                        + ", ".join(sorted(self.allowed_fields.keys()))
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        model_field = self.allowed_fields[requested_field]

        tzinfo = ZoneInfo(self.timezone_name)
        start_of_month, end_of_month = local_month_bounds(year, month, tzinfo)

        filters = {self.module_lookup: module_id}
        queryset = (
            self.data_model.objects.filter(
                createdAt__gte=start_of_month,
                createdAt__lte=end_of_month,
                **filters,
            )
            .annotate(local_date=TruncDate("createdAt", tzinfo=tzinfo))
            .values("local_date")
            .annotate(
                daily_sum=Coalesce(
                    Sum(Cast(F(model_field), FloatField())),
                    Value(0.0, output_field=FloatField()),
                )
            )
        )

        day_totals: Dict[date, float] = {}
        for row in queryset:
            local_date = row.get("local_date")
            if local_date is None:
                continue
            if isinstance(local_date, datetime):
                local_date = local_date.date()
            day_totals[local_date] = float(row.get("daily_sum") or 0.0)

        week_definitions = month_weeks(year, month)
        weekday_labels = week_label_days()
        week_payloads = []
        for definition in week_definitions:
            week_payloads.append(
                {
                    "week": definition.week,
                    "range": {
                        "start": definition.start,
                        "end": definition.end,
                    },
                    "days": list(weekday_labels),
                    "data": [0.0] * 7,
                }
            )

        for current_day, total in day_totals.items():
            bucket_index = week_index_for_day(current_day.day, week_definitions)
            if bucket_index is None:
                continue
            weekday_index = current_day.weekday()
            week_payloads[bucket_index]["data"][weekday_index] = float(total)

        for week_payload in week_payloads:
            week_values = week_payload["data"] or [0.0] * 7
            week_sum = float(sum(week_values))
            week_avg = week_sum / 7.0 if week_values else 0.0
            week_min = float(min(week_values)) if week_values else 0.0
            week_max = float(max(week_values)) if week_values else 0.0

            # Show Total/Average for production and energy fields
            if requested_field in ("production", "energy", "consomation", "consommation"):
                week_payload["totals"] = {"total": week_sum, "avg": week_avg}
            else:
                week_payload["totals"] = {"min": week_min, "max": week_max}

        response_payload = {
            "year": year,
            "month": month,
            "entity": self.entity_name,
            "module_id": module_id,
            "field": requested_field,
            "weeks": week_payloads,
        }

        serializer = WeeklyByMonthResponseSerializer(response_payload)
        return Response(serializer.data)


class PanneauWeeklyByMonthView(WeeklyByMonthBaseView):
    entity_name = "panneau"
    data_model = PanneauData
    module_lookup = "panneau__module_id"
    allowed_fields = {
        "production": "production",
        "tension": "tension",
        "puissance": "puissance",
        "courant": "courant",
    }
    default_field = "production"


class BatteryWeeklyByMonthView(WeeklyByMonthBaseView):
    entity_name = "battery"
    data_model = BatteryData
    module_lookup = "battery__module_id"
    allowed_fields = {
        "energy": "energy",
        "tension": "tension",
        "puissance": "puissance",
        "courant": "courant",
        "pourcentage": "pourcentage",
    }
    default_field = "energy"


class PriseWeeklyByMonthView(WeeklyByMonthBaseView):
    entity_name = "prise"
    data_model = PriseData
    module_lookup = "prise__module_id"
    allowed_fields = {
        "consomation": "consomation",
        "tension": "tension",
        "puissance": "puissance",
        "courant": "courant",
    }
    default_field = "consomation"



# ====================================================DAILY=======================================


class BaseDailyAPIView(APIView):
    entity: str = ""
    data_model = None
    owner_model = None
    fk_name: str = ""
    default_field: str = ""
    allowed_fields: Iterable[str] = ()

    def _validate_field(self, field: str) -> str:
        if field not in self.allowed_fields:
            allowed = ", ".join(sorted(self.allowed_fields))
            raise ValidationError(
                {"field": f"Invalid field '{field}'. Allowed values: {allowed}."}
            )
        return field

    @staticmethod
    def _parse_step(step_param: str | None) -> int | None:
        if not step_param:
            return None
        if not step_param.endswith("m"):
            raise ValidationError({"step": "Step must end with 'm' (e.g. 5m, 10m, 15m)."})
        try:
            minutes = int(step_param[:-1])
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValidationError({"step": "Invalid step value."}) from exc
        if minutes not in {5, 10, 15}:
            raise ValidationError({"step": "Step must be one of 5m, 10m or 15m."})
        return minutes

    def get_owner(self, module_id: str):
        assert self.owner_model is not None
        return get_object_or_404(self.owner_model, module__id=module_id)

    def get(self, request, module_id: str, year: int, month: int, day: int):
        field = request.query_params.get("field", self.default_field)
        field = self._validate_field(field)

        step_minutes = self._parse_step(request.query_params.get("step"))
        owner = self.get_owner(module_id)
        start, end = local_day_bounds(year, month, day)

        data, base_stats = fetch_daily_points(
            self.data_model,
            self.fk_name,
            owner,
            field,
            start,
            end,
        )

        if step_minutes:
            data = group_points_by_step(data, field, step_minutes)
            numeric_values = [point[field] for point in data if point[field] is not None]
            total = float(sum(numeric_values)) if numeric_values else 0.0
            count = len(numeric_values)
        else:
            numeric_values = [point[field] for point in data if point[field] is not None]
            if numeric_values:
                total = float(base_stats.get("total", 0.0))
                count = int(base_stats.get("count", 0))
            else:
                total = 0.0
                count = 0

        avg = float(total / count) if count else 0.0
        min_value = float(min(numeric_values)) if numeric_values else 0.0
        max_value = float(max(numeric_values)) if numeric_values else 0.0

        # Show Total/Average for production, energy, and consumption fields
        if field in ("production", "energy", "consomation", "consommation"):
            stats_block = {"total": total, "average": avg, "count": count}
        else:
            stats_block = {
                "min": min_value,
                "max": max_value,
                "average": avg,
                "count": count,
            }

        payload = {
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "timezone": INDIAN_ANTANARIVO,
            "entity": self.entity,
            "module_id": module_id,
            "field": field,
            "data": data,
            "stats": stats_block,
        }

        return Response(payload, status=status.HTTP_200_OK)


class PanneauDailyAPIView(BaseDailyAPIView):
    entity = "panneau"
    data_model = PanneauData
    owner_model = Panneau
    fk_name = "panneau"
    default_field = "production"
    allowed_fields = {"production", "tension", "puissance", "courant"}


class BatteryDailyAPIView(BaseDailyAPIView):
    entity = "battery"
    data_model = BatteryData
    owner_model = Battery
    fk_name = "battery"
    default_field = "energy"
    allowed_fields = {"energy", "pourcentage", "tension", "puissance", "courant"}


class PriseDailyAPIView(BaseDailyAPIView):
    entity = "prise"
    data_model = PriseData
    owner_model = Prise
    fk_name = "prise"
    default_field = "consomation"
    allowed_fields = {"consomation", "tension", "puissance", "courant"}

