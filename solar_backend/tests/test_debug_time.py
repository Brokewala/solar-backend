from datetime import datetime, timedelta

from rest_framework.test import APITestCase


class DebugTimeEndpointTest(APITestCase):
    def test_returns_local_and_utc_times(self):
        response = self.client.get("/debug/time")
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertIn("now_local", payload)
        self.assertIn("now_utc", payload)

        local_dt = datetime.fromisoformat(payload["now_local"])
        utc_dt = datetime.fromisoformat(payload["now_utc"])

        self.assertIsNotNone(local_dt.tzinfo)
        self.assertEqual(local_dt.tzinfo.utcoffset(local_dt), timedelta(hours=3))
        self.assertTrue(payload["now_local"].endswith("+03:00"))

        self.assertIsNotNone(utc_dt.tzinfo)
        self.assertEqual(utc_dt.tzinfo.utcoffset(utc_dt), timedelta())
        self.assertTrue(payload["now_utc"].endswith("+00:00"))
