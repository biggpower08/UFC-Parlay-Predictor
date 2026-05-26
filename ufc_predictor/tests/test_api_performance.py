import unittest
from unittest.mock import patch

from ufc_predictor.api import app as api_app


class TestApiPerformance(unittest.TestCase):
    def setUp(self):
        api_app._health_cache = None
        api_app._health_cache_time = 0.0

    def test_health_uses_short_ttl_cache(self):
        with patch.object(api_app, "_database_ready", return_value=True) as db_ready:
            with patch.object(api_app, "model_available", return_value=True):
                first = api_app.health()
                second = api_app.health()

        self.assertTrue(first["prediction_ready"])
        self.assertTrue(second["prediction_ready"])
        self.assertEqual(db_ready.call_count, 1)

    def test_health_force_bypasses_cache(self):
        with patch.object(api_app, "_database_ready", return_value=True) as db_ready:
            with patch.object(api_app, "model_available", return_value=True):
                api_app.health()
                api_app.health(force=True)

        self.assertEqual(db_ready.call_count, 2)


if __name__ == "__main__":
    unittest.main()
