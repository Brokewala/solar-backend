from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List

from django.db.models import F, Sum, Value
from django.db.models import FloatField
from django.db.models.functions import Cast, Coalesce, TruncDay
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from battery.models import Battery, BatteryData
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData
from solar_backend.timezone_utils import (
    local_month_bounds,
    local_week_slices_for_month,
    resolve_timezone,
    safe_float,
)


WEEKDAY_LABELS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
ENTITY_ORDER = {"panneau": 0, "batterie": 1, "prise": 2}


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
        totals[day_key] = safe_float(entry.get("total"))
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
