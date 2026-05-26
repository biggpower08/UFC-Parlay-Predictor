import unittest

from ufc_predictor.features.feature_engineering import build_master_df, compare_fighters
from ufc_predictor.features.matchup_builder import build_matchup_features, features_to_vector
from ufc_predictor.models.sklearn.predictor import model_available, predict_matchup
from ufc_predictor.models.ensemble.predictor import predict_ensemble
from ufc_predictor.pipeline import run_prediction
from ufc_predictor.utils.helpers import normalize_name


class TestPredictionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master = build_master_df()
        cls.row = cls.master[
            cls.master["_search_name"] == normalize_name("Islam Makhachev")
        ]
        if cls.row.empty:
            cls.skipTest("Islam Makhachev not in database")
        cls.f1 = cls.row.iloc[0]
        cls.row2 = cls.master[
            cls.master["_search_name"] == normalize_name("Alex Pereira")
        ]
        if cls.row2.empty:
            cls.skipTest("Alex Pereira not in database")
        cls.f2 = cls.row2.iloc[0]

    def test_matchup_features_shape(self):
        feats = build_matchup_features(self.f1, self.f2)
        vec = features_to_vector(feats)
        self.assertGreater(len(vec), 10)

    def test_compare_fighters(self):
        comp = compare_fighters(self.f1, self.f2)
        self.assertIn("stats1", comp)
        self.assertIn("Elo", comp["stats1"])
        self.assertIn("Elo Available", comp["stats1"])
        self.assertIn("Elo Source", comp["stats1"])

    def test_run_prediction(self):
        comp, pred, summary = run_prediction(self.f1, self.f2)
        self.assertIn("winner", pred)
        self.assertIn("prob_a", pred)
        self.assertIn("diagnostics", pred)
        self.assertIn("elo", pred["diagnostics"])
        self.assertTrue(summary)
        self.assertIn("matchup", summary)
        self.assertIn("biggest danger", summary)
        self.assertNotIn("guaranteed", summary.lower())
        self.assertNotIn("lock", summary.lower())

    @unittest.skipUnless(model_available(), "model not trained")
    def test_sklearn_predict(self):
        out = predict_matchup(self.f1, self.f2)
        self.assertIsNotNone(out)
        self.assertGreaterEqual(out["prob_a_wins"], 0)
        self.assertLessEqual(out["prob_a_wins"], 1)
        self.assertTrue(out["diagnostics"]["elo_features_present"])
        self.assertIn("delta_elo", out["features"])
        self.assertIn("elo_expected_a", out["features"])

    @unittest.skipUnless(model_available(), "model not trained")
    def test_elo_changes_model_and_ensemble_signal_for_identical_fighters(self):
        high_elo = self.f1.copy()
        low_elo = self.f1.copy()
        for row, name, elo in ((high_elo, "High Elo Test", 1300), (low_elo, "Low Elo Test", 900)):
            row["name"] = name
            row["elo"] = elo
            row["elo_source"] = "computed"
            row["elo_fights_count"] = 10
            row["points_p4p"] = 0
            row["rank_p4p"] = 0
            row["points_dom"] = 0
            row["rank_dom"] = 0

        high_vs_low_features = build_matchup_features(high_elo, low_elo)
        low_vs_high_features = build_matchup_features(low_elo, high_elo)
        self.assertEqual(high_vs_low_features["delta_elo"], 400)
        self.assertEqual(low_vs_high_features["delta_elo"], -400)

        high_vs_low = predict_matchup(high_elo, low_elo)
        low_vs_high = predict_matchup(low_elo, high_elo)
        self.assertGreater(high_vs_low["prob_a_wins"], low_vs_high["prob_a_wins"])

        high_ensemble = predict_ensemble(high_elo, low_elo, compare_fighters(high_elo, low_elo))
        low_ensemble = predict_ensemble(low_elo, high_elo, compare_fighters(low_elo, high_elo))
        self.assertTrue(high_ensemble["signals"]["elo"]["available"])
        self.assertGreater(high_ensemble["prob_a"], low_ensemble["prob_a"])


if __name__ == "__main__":
    unittest.main()
