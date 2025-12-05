from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase
from rest_framework.test import APIClient

from battery.models import Battery, BatteryData
from module.models import Modules
from panneau.models import Panneau, PanneauData
from prise.models import Prise, PriseData
from users.models import ProfilUser


class DailyEndpointsTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.client = APIClient()
        self.tz = ZoneInfo("Indian/Antananarivo")

        self.user = ProfilUser.objects.create_user(
            id="user-test",
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.module = Modules.objects.create(id="module-test", user=self.user)
        self.panneau = Panneau.objects.create(id="panneau-test", module=self.module)
        self.battery = Battery.objects.create(id="battery-test", module=self.module)
        self.prise = Prise.objects.create(id="prise-test", module=self.module)

        self._create_sample_data()

    def _create_sample_data(self):
        target_day = datetime(2025, 3, 12, tzinfo=self.tz)

        def dt(hour: int, minute: int) -> datetime:
            return target_day.replace(hour=hour, minute=minute)

        def create_with_timestamp(model, created_at: datetime, **fields):
            obj = model.objects.create(**fields)
            model.objects.filter(pk=obj.pk).update(createdAt=created_at)
            return obj

        # Panneau data
        create_with_timestamp(
            PanneauData,
            dt(0, 5),
            id="panneau-data-1",
            panneau=self.panneau,
            production="1.2",
            tension="10.0",
        )
        create_with_timestamp(
            PanneauData,
            dt(12, 15),
            id="panneau-data-2",
            panneau=self.panneau,
            production="2.3",
            tension="12.0",
        )
        create_with_timestamp(
            PanneauData,
            dt(23, 55),
            id="panneau-data-3",
            panneau=self.panneau,
            production="0.5",
            tension="11.0",
        )
        create_with_timestamp(
            PanneauData,
            dt(0, 1) + timedelta(days=1),
            id="panneau-data-4",
            panneau=self.panneau,
            production="9.9",
        )

        # Battery data
        create_with_timestamp(
            BatteryData,
            dt(1, 0),
            id="battery-data-1",
            battery=self.battery,
            energy="5.5",
            courant="1.0",
        )
        create_with_timestamp(
            BatteryData,
            dt(1, 5),
            id="battery-data-2",
            battery=self.battery,
            energy="6.5",
            courant="1.5",
        )

        # Prise data
        create_with_timestamp(
            PriseData,
            dt(6, 30),
            id="prise-data-1",
            prise=self.prise,
            consomation="0.8",
            puissance="2.0",
        )

    def test_panneau_daily_returns_only_selected_day(self):
        url = "/api/panneau/module-test/2025/3/12/daily"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["entity"], "panneau")
        self.assertEqual(payload["field"], "production")
        self.assertEqual(payload["timezone"], "Indian/Antananarivo")
        self.assertEqual(payload["stats"]["count"], 3)
        self.assertAlmostEqual(payload["stats"]["total"], 1.2 + 2.3 + 0.5)
        self.assertAlmostEqual(payload["stats"]["avg"], (1.2 + 2.3 + 0.5) / 3)

        hours = [point["hour_label"] for point in payload["data"]]
        self.assertEqual(hours, ["00:05", "12:15", "23:55"])

    def test_battery_daily_with_field_override_and_step(self):
        url = "/api/battery/module-test/2025/3/12/daily"
        response = self.client.get(url, {"field": "courant", "step": "5m"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["entity"], "battery")
        self.assertEqual(payload["field"], "courant")
        self.assertEqual(payload["stats"]["count"], 2)
        self.assertAlmostEqual(payload["stats"]["total"], 1.0 + 1.5)
        self.assertAlmostEqual(payload["stats"]["avg"], (1.0 + 1.5) / 2)
        self.assertEqual(len(payload["data"]), 2)

    def test_prise_daily_invalid_field(self):
        url = "/api/prise/module-test/2025/3/12/daily"
        response = self.client.get(url, {"field": "unknown"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("field", response.json())

    def test_invalid_step_value(self):
        url = "/api/panneau/module-test/2025/3/12/daily"
        response = self.client.get(url, {"step": "7m"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("step", response.json())

