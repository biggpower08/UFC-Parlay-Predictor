import unittest

import pandas as pd

from ufc_predictor.models.elo.elo_engine import build_elo_fight_counts, compute_elo_ratings


class TestEloEngine(unittest.TestCase):
    def test_elo_changes_after_completed_fights(self):
        fights = pd.DataFrame(
            [
                {"event": "Newest", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "win"},
                {"event": "Middle", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "win"},
                {"event": "Oldest", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "win"},
            ]
        )

        fights_elo, ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
        fight_counts = build_elo_fight_counts(fights_elo)

        self.assertGreater(ratings["Alpha Fighter"], 1000)
        self.assertLess(ratings["Beta Fighter"], 1000)
        self.assertEqual(elo_by_search["alpha fighter"], ratings["Alpha Fighter"])
        self.assertGreaterEqual(peak_elo["Alpha Fighter"], ratings["Alpha Fighter"])
        self.assertEqual(fight_counts["alpha fighter"], 3)
        self.assertEqual(fight_counts["beta fighter"], 3)


if __name__ == "__main__":
    unittest.main()
