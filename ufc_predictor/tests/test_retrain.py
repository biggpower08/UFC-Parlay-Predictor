import unittest

from ufc_predictor.features.feature_engineering import build_master_df
from ufc_predictor.features.matchup_builder import build_training_dataset
from ufc_predictor.data_sources.fights import load_fights


class TestRetrainPipeline(unittest.TestCase):
    def test_training_dataset_builds(self):
        master = build_master_df()
        fights = load_fights()
        X, y = build_training_dataset(fights, master)
        self.assertGreater(len(y), 100)
        self.assertGreater(X.shape[1], 15)


if __name__ == "__main__":
    unittest.main()
