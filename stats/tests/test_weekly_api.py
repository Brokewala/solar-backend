from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import TestCase
from rest_framework.test import APIClient

from module.models import Modules
from panneau.models import Panneau, PanneauData
from users.models import ProfilUser


class PanneauWeeklyByMonthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = ProfilUser.objects.create_user(
            email="user@example.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.module = Modules.objects.create(user=self.user)
        self.panneau = Panneau.objects.create(module=self.module)
        self.tz = ZoneInfo("Indian/Antananarivo")

    def _create_production(self, day: int, production: float):
        timestamp = datetime(2025, 3, day, 10, 0, tzinfo=self.tz)
        record = PanneauData.objects.create(
            panneau=self.panneau,
            production=str(production),
            tension="0",
            puissance="0",
            courant="0",
        )
        PanneauData.objects.filter(pk=record.pk).update(createdAt=timestamp)

    def test_weekly_structure_and_totals(self):
        self._create_production(3, 10)
        self._create_production(7, 4)
        self._create_production(9, 5)
        self._create_production(16, 8)
        self._create_production(23, 12)
        self._create_production(30, 3)

        response = self.client.get(
            f"/api/panneau/{self.module.id}/2025/3/weekly"
        )
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["entity"], "panneau")
        self.assertEqual(payload["field"], "production")
        self.assertEqual(payload["month"], 3)
        self.assertEqual(payload["year"], 2025)

        weeks = payload["weeks"]
        self.assertEqual(len(weeks), 5)

        first_week = weeks[0]
        self.assertEqual(first_week["range"], {"start": "2025-03-01", "end": "2025-03-07"})
        self.assertEqual(first_week["days"], ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"])
        self.assertEqual(first_week["data"][0], 10.0)  # Monday 3rd
        self.assertEqual(first_week["data"][4], 4.0)   # Friday 7th
        self.assertEqual(first_week["totals"], {"sum": 14.0, "avg": 2.0})

        fifth_week = weeks[4]
        self.assertEqual(fifth_week["range"], {"start": "2025-03-29", "end": "2025-03-31"})
        self.assertEqual(fifth_week["data"][6], 3.0)  # Sunday 30th
        self.assertAlmostEqual(fifth_week["totals"]["sum"], 3.0)
        self.assertAlmostEqual(fifth_week["totals"]["avg"], 3.0 / 7.0)
