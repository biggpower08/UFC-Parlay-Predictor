import unittest

from ufc_predictor.features.feature_engineering import build_master_df, compare_fighters
from ufc_predictor.features.matchup_builder import build_matchup_features, features_to_vector
from ufc_predictor.models.sklearn.predictor import model_available, predict_matchup
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

    def test_run_prediction(self):
        comp, pred, summary = run_prediction(self.f1, self.f2)
        self.assertIn("winner", pred)
        self.assertIn("prob_a", pred)
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


if __name__ == "__main__":
    unittest.main()
