from __future__ import annotations

from typing import Iterable

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from battery.models import Battery, BatteryData
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData

from solar_backend.utils_daily import fetch_daily_points, group_points_by_step
from solar_backend.utils_tz import INDIAN_ANTANARIVO, local_day_bounds


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

        payload = {
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "timezone": INDIAN_ANTANARIVO,
            "entity": self.entity,
            "module_id": module_id,
            "field": field,
            "data": data,
            "stats": {
                "count": count,
                "total": total,
                "avg": avg,
            },
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

