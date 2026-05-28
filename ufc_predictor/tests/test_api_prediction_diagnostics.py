import unittest

import ufc_predictor.api.app as api_app
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
        self.assertIn("prop_reads", payload["analysis"])
        self.assertTrue(payload["analysis"]["summary"])


if __name__ == "__main__":
    unittest.main()


def test_cross_division_request_is_not_blocked_when_legacy_flag_is_false(monkeypatch):
    def fake_resolve_fighter(name, **kwargs):
        return {"name": name, "weight_class": "Lightweight" if name == "Alpha Fighter" else "Heavyweight"}

    comparison = {
        "stats1": {"Name": "Alpha Fighter", "Weight Class": "Lightweight"},
        "stats2": {"Name": "Heavy Fighter", "Weight Class": "Heavyweight"},
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.6, "prob_a": 0.6}
    analysis = {
        "summary": "Prediction shown with cross-division context.",
        "sections": [],
        "matchup_type": {"label": "Cross-division matchup", "severity": "high", "explanation": "Different divisions."},
        "prop_reads": [
            {
                "id": "volatility_prop_warning",
                "category": "warning",
                "label": "Volatility prop warning",
                "prop_style": "Cross-division matchup: prop-style reads are less reliable.",
                "confidence": "low",
                "support_level": "limited_data",
                "explanation": "Different divisions.",
                "caution": "Cross-division matchup: prop-style reads are less reliable.",
            }
        ],
    }

    monkeypatch.setattr(api_app, "resolve_fighter", fake_resolve_fighter)
    monkeypatch.setattr(api_app, "run_prediction", lambda fighter_a, fighter_b: (comparison, prediction, "summary"))
    monkeypatch.setattr(api_app, "build_fight_analysis", lambda comparison, prediction: analysis)
    monkeypatch.setattr(api_app, "save_prediction", lambda *args, **kwargs: "prediction-id")

    payload = api_app.predict(
        PredictRequest(
            fighter_a="Alpha Fighter",
            fighter_b="Heavy Fighter",
            allow_scrape=False,
            confirmed_a=True,
            confirmed_b=True,
            allow_cross_division=False,
        )
    )

    assert payload["analysis"]["matchup_type"]["label"] == "Cross-division matchup"
    assert payload["analysis"]["prop_reads"]
    assert payload["prediction_id"] == "prediction-id"
