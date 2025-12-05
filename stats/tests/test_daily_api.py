from __future__ import annotations

from datetime import datetime
from typing import Iterable
from zoneinfo import ZoneInfo

from django.urls import reverse
from rest_framework.test import APITestCase

from battery.models import Battery, BatteryData
from module.models import Modules
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData
from users.models import ProfilUser


class DailyStatsAPITests(APITestCase):
    tz = ZoneInfo("Indian/Antananarivo")

    def setUp(self) -> None:
        self.owner = ProfilUser.objects.create_user(
            email="owner@example.com",
            password="password123",
            first_name="Owner",
            last_name="User",
        )
        self.module = Modules.objects.create(user=self.owner)
        self.other_module = Modules.objects.create(user=self.owner)
        self.module_id = str(self.module.id)
        self.other_module_id = str(self.other_module.id)

        self.panneau = Panneau.objects.create(module=self.module)
        self.other_panneau = Panneau.objects.create(module=self.other_module)

        self.battery = Battery.objects.create(module=self.module)
        self.other_battery = Battery.objects.create(module=self.other_module)

        self.prise = Prise.objects.create(module=self.module)
        self.other_prise = Prise.objects.create(module=self.other_module)

    def _create_data_point(
        self,
        model,
        fk_name: str,
        owner_obj,
        field: str,
        value: str,
        timestamp: datetime,
    ):
        instance = model.objects.create(**{fk_name: owner_obj, field: value})
        model.objects.filter(pk=instance.pk).update(
            createdAt=timestamp,
            updatedAt=timestamp,
        )
        return instance

    def _assert_daily_response(
        self,
        response_data: dict,
        *,
        entity: str,
        module_id: str,
        field: str,
        expected_values: Iterable[tuple[datetime, float]],
    ) -> None:
        self.assertEqual(response_data["entity"], entity)
        self.assertEqual(response_data["module_id"], module_id)
        self.assertEqual(response_data["field"], field)
        self.assertEqual(response_data["timezone"], "Indian/Antananarivo")

        expected_list = list(expected_values)
        returned_points = response_data["data"]
        self.assertEqual(len(returned_points), len(expected_list))

        total_expected = 0.0
        for entry, (expected_dt, expected_value) in zip(returned_points, expected_list):
            timestamp = datetime.fromisoformat(entry["timestamp"])
            local_timestamp = timestamp.astimezone(self.tz)

            self.assertEqual(local_timestamp.date().isoformat(), response_data["date"])
            self.assertEqual(entry["hour_label"], expected_dt.astimezone(self.tz).strftime("%H:%M"))
            self.assertAlmostEqual(entry[field], expected_value)
            total_expected += expected_value

        stats = response_data["stats"]
        self.assertEqual(stats["count"], len(expected_list))
        self.assertAlmostEqual(stats["total"], total_expected)
        expected_avg = total_expected / len(expected_list) if expected_list else 0.0
        self.assertAlmostEqual(stats["avg"], expected_avg)

    def test_panneau_daily_endpoint_filters_day_and_computes_stats(self):
        query_day = datetime(2024, 5, 1, tzinfo=self.tz)
        same_day_points = [
            (datetime(2024, 5, 1, 8, 15, tzinfo=self.tz), "1.5"),
            (datetime(2024, 5, 1, 10, 45, tzinfo=self.tz), "2.0"),
        ]
        for ts, value in same_day_points:
            self._create_data_point(
                PanneauData,
                "panneau",
                self.panneau,
                "production",
                value,
                ts,
            )

        # Data outside of the queried day or for another module should be ignored
        self._create_data_point(
            PanneauData,
            "panneau",
            self.panneau,
            "production",
            "5.5",
            datetime(2024, 4, 30, 23, 59, tzinfo=self.tz),
        )
        self._create_data_point(
            PanneauData,
            "panneau",
            self.other_panneau,
            "production",
            "9.9",
            datetime(2024, 5, 1, 12, tzinfo=self.tz),
        )

        url = reverse(
            "panneau-daily",
            kwargs={
                "module_id": self.module_id,
                "year": query_day.year,
                "month": query_day.month,
                "day": query_day.day,
            },
        )
        response = self.client.get(url, {"field": "production"})
        self.assertEqual(response.status_code, 200)

        expected_sequence = [
            (same_day_points[0][0], float(same_day_points[0][1])),
            (same_day_points[1][0], float(same_day_points[1][1])),
        ]
        self._assert_daily_response(
            response.data,
            entity="panneau",
            module_id=self.module_id,
            field="production",
            expected_values=expected_sequence,
        )

    def test_battery_daily_endpoint_uses_module_owner_and_local_labels(self):
        query_day = datetime(2024, 6, 10, tzinfo=self.tz)
        # Use UTC timestamps to ensure conversion to local timezone happens
        same_day_points = [
            (datetime(2024, 6, 10, 4, 0, tzinfo=ZoneInfo("UTC")), "3.0"),
            (datetime(2024, 6, 10, 6, 30, tzinfo=ZoneInfo("UTC")), "1.5"),
        ]
        for ts, value in same_day_points:
            self._create_data_point(
                BatteryData,
                "battery",
                self.battery,
                "energy",
                value,
                ts,
            )

        # Data for the other battery should not leak into the response
        self._create_data_point(
            BatteryData,
            "battery",
            self.other_battery,
            "energy",
            "7.0",
            datetime(2024, 6, 10, 5, 0, tzinfo=ZoneInfo("UTC")),
        )

        url = reverse(
            "battery-daily",
            kwargs={
                "module_id": self.module_id,
                "year": query_day.year,
                "month": query_day.month,
                "day": query_day.day,
            },
        )
        response = self.client.get(url, {"field": "energy"})
        self.assertEqual(response.status_code, 200)

        expected_sequence = [
            (
                same_day_points[0][0].astimezone(self.tz),
                float(same_day_points[0][1]),
            ),
            (
                same_day_points[1][0].astimezone(self.tz),
                float(same_day_points[1][1]),
            ),
        ]
        self._assert_daily_response(
            response.data,
            entity="battery",
            module_id=self.module_id,
            field="energy",
            expected_values=expected_sequence,
        )

    def test_prise_daily_endpoint_returns_expected_payload(self):
        query_day = datetime(2024, 7, 20, tzinfo=self.tz)
        same_day_points = [
            (datetime(2024, 7, 20, 0, 5, tzinfo=self.tz), "0.5"),
            (datetime(2024, 7, 20, 22, 45, tzinfo=self.tz), "1.75"),
        ]
        for ts, value in same_day_points:
            self._create_data_point(
                PriseData,
                "prise",
                self.prise,
                "consomation",
                value,
                ts,
            )

        self._create_data_point(
            PriseData,
            "prise",
            self.prise,
            "consomation",
            "12.0",
            datetime(2024, 7, 21, 0, 0, tzinfo=self.tz),
        )
        self._create_data_point(
            PriseData,
            "prise",
            self.other_prise,
            "consomation",
            "8.0",
            datetime(2024, 7, 20, 12, 0, tzinfo=self.tz),
        )

        url = reverse(
            "prise-daily",
            kwargs={
                "module_id": self.module_id,
                "year": query_day.year,
                "month": query_day.month,
                "day": query_day.day,
            },
        )
        response = self.client.get(url, {"field": "consomation"})
        self.assertEqual(response.status_code, 200)

        expected_sequence = [
            (same_day_points[0][0], float(same_day_points[0][1])),
            (same_day_points[1][0], float(same_day_points[1][1])),
        ]
        self._assert_daily_response(
            response.data,
            entity="prise",
            module_id=self.module_id,
            field="consomation",
            expected_values=expected_sequence,
        )

    def test_daily_views_enforce_allowed_fields_configuration(self):
        from stats.views import (
            BatteryDailyAPIView,
            PanneauDailyAPIView,
            PriseDailyAPIView,
        )

        self.assertEqual(PanneauDailyAPIView.default_field, "production")
        self.assertSetEqual(
            set(PanneauDailyAPIView.allowed_fields),
            {"production", "tension", "puissance", "courant"},
        )

        self.assertEqual(BatteryDailyAPIView.default_field, "energy")
        self.assertSetEqual(
            set(BatteryDailyAPIView.allowed_fields),
            {"energy", "pourcentage", "tension", "puissance", "courant"},
        )

        self.assertEqual(PriseDailyAPIView.default_field, "consomation")
        self.assertSetEqual(
            set(PriseDailyAPIView.allowed_fields),
            {"consomation", "tension", "puissance", "courant"},
        )

    def test_daily_views_use_default_field_when_missing(self):
        query_day = datetime(2024, 8, 5, 12, 0, tzinfo=self.tz)

        self._create_data_point(
            PanneauData,
            "panneau",
            self.panneau,
            "production",
            "4.2",
            query_day,
        )

        url = reverse(
            "panneau-daily",
            kwargs={
                "module_id": self.module_id,
                "year": query_day.year,
                "month": query_day.month,
                "day": query_day.day,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        expected_sequence = [(query_day, 4.2)]
        self._assert_daily_response(
            response.data,
            entity="panneau",
            module_id=self.module_id,
            field="production",
            expected_values=expected_sequence,
        )

    def test_daily_views_reject_unknown_field(self):
        query_day = datetime(2024, 9, 10, tzinfo=self.tz)

        url = reverse(
            "prise-daily",
            kwargs={
                "module_id": self.module_id,
                "year": query_day.year,
                "month": query_day.month,
                "day": query_day.day,
            },
        )

        response = self.client.get(url, {"field": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("field", response.data)
        detail = response.data["field"]
        if isinstance(detail, (list, tuple)):
            messages = [str(item) for item in detail]
        else:
            messages = [str(detail)]
        self.assertTrue(any("Invalid field" in msg for msg in messages))
