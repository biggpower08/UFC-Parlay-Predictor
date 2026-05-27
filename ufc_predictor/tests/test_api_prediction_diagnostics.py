import unittest

from ufc_predictor.api.app import PredictRequest, predict
from ufc_predictor.models.sklearn.predictor import model_available


class TestApiPredictionDiagnostics(unittest.TestCase):
    @unittest.skipUnless(model_available(), "model not trained")
    def test_debug_prediction_includes_elo_diagnostics(self):
        payload = predict(
            PredictRequest(
                fighter_a="Islam Makhachev",
                fighter_b="Charles Oliveira",
                allow_scrape=False,
                confirmed_a=True,
                confirmed_b=True,
                debug=True,
            )
        )

        diagnostics = payload["prediction"]["diagnostics"]
        self.assertIn("elo", diagnostics)
        self.assertIn("sklearn", diagnostics)
        self.assertIn("delta_elo", diagnostics["elo"])
        self.assertTrue(diagnostics["sklearn"]["elo_features_present"])

    @unittest.skipUnless(model_available(), "model not trained")
    def test_public_prediction_hides_diagnostics(self):
        payload = predict(
            PredictRequest(
                fighter_a="Islam Makhachev",
                fighter_b="Charles Oliveira",
                allow_scrape=False,
                confirmed_a=True,
                confirmed_b=True,
                debug=False,
            )
        )

        self.assertNotIn("diagnostics", payload["prediction"])
        self.assertIn("analysis", payload)
        self.assertIn("sections", payload["analysis"])
        self.assertTrue(payload["analysis"]["summary"])


if __name__ == "__main__":
    unittest.main()
