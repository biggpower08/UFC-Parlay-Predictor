import unittest

import pandas as pd

from ufc_predictor.models.elo.elo_engine import (
    build_elo_fight_counts,
    compute_elo_ratings,
    expected_score,
    prepare_fights_chronological,
    update_elo_draw,
    update_elo_win,
)


class TestEloEngine(unittest.TestCase):
    def test_expected_score_equal_ratings(self):
        self.assertAlmostEqual(expected_score(1000, 1000), 0.5)

    def test_higher_rated_fighter_expected_above_half(self):
        self.assertGreater(expected_score(1200, 1000), 0.5)

    def test_favorite_win_gains_less_than_underdog_upset(self):
        favorite_after, _ = update_elo_win(1200, 1000, k_factor=40)
        underdog_after, _ = update_elo_win(1000, 1200, k_factor=40)

        self.assertLess(favorite_after - 1200, underdog_after - 1000)

    def test_simple_win_loss_is_zero_sum(self):
        winner_after, loser_after = update_elo_win(1000, 1000, k_factor=40)

        self.assertAlmostEqual(winner_after - 1000, 1000 - loser_after)

    def test_draw_moves_ratings_toward_each_other(self):
        high_after, low_after = update_elo_draw(1200, 1000, k_factor=40)

        self.assertLess(high_after, 1200)
        self.assertGreater(low_after, 1000)

    def test_event_date_sorting_is_oldest_to_newest(self):
        fights = pd.DataFrame(
            [
                {"event": "New", "event_date": "2024-01-01", "fighter_1": "A", "fighter_2": "B", "result": "win"},
                {"event": "Old", "event_date": "2020-01-01", "fighter_1": "C", "fighter_2": "D", "result": "win"},
            ]
        )

        ordered = prepare_fights_chronological(fights)

        self.assertEqual(ordered.iloc[0]["event"], "Old")
        self.assertEqual(ordered.iloc[0]["elo_order_source"], "event_date")

    def test_same_event_uses_fight_order_when_available(self):
        fights = pd.DataFrame(
            [
                {"event": "Same", "event_date": "2020-01-01", "fight_order": 2, "fighter_1": "A", "fighter_2": "B", "result": "win"},
                {"event": "Same", "event_date": "2020-01-01", "fight_order": 1, "fighter_1": "C", "fighter_2": "D", "result": "win"},
            ]
        )

        ordered = prepare_fights_chronological(fights)

        self.assertEqual(ordered.iloc[0]["fighter_1"], "C")

    def test_source_order_fallback_reverses_when_dates_missing(self):
        fights = pd.DataFrame(
            [
                {"event": "Newest", "fighter_1": "A", "fighter_2": "B", "result": "win"},
                {"event": "Oldest", "fighter_1": "C", "fighter_2": "D", "result": "win"},
            ]
        )

        ordered = prepare_fights_chronological(fights)

        self.assertEqual(ordered.iloc[0]["event"], "Oldest")
        self.assertEqual(ordered.iloc[0]["elo_order_source"], "source_order_inferred")

    def test_fighter_1_win_updates_fighter_1_upward_and_tracks_trace(self):
        fights = pd.DataFrame(
            [{"event": "One", "event_date": "2020-01-01", "fighter_1": "Alpha", "fighter_2": "Beta", "result": "win"}]
        )

        fights_elo, ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)

        self.assertGreater(ratings["Alpha"], 1000)
        self.assertLess(ratings["Beta"], 1000)
        self.assertEqual(elo_by_search["alpha"], ratings["Alpha"])
        self.assertEqual(peak_elo["Alpha"], ratings["Alpha"])
        self.assertEqual(fights_elo.iloc[0]["fighter_1_elo_change"], 20)
        self.assertEqual(fights_elo.iloc[0]["fighter_2_elo_change"], -20)
        self.assertEqual(fights_elo.iloc[0]["elo_result_type"], "win")
        self.assertAlmostEqual(fights_elo.iloc[0]["elo_expected_fighter_1"], 0.5)

    def test_explicit_winner_field_can_override_fighter_1_relative_result(self):
        fights = pd.DataFrame(
            [
                {
                    "event": "One",
                    "event_date": "2020-01-01",
                    "fighter_1": "Alpha",
                    "fighter_2": "Beta",
                    "winner_name": "Beta",
                    "loser_name": "Alpha",
                    "result": "win",
                }
            ]
        )

        _fights_elo, ratings, _peak_elo, _elo_by_search = compute_elo_ratings(fights)

        self.assertLess(ratings["Alpha"], 1000)
        self.assertGreater(ratings["Beta"], 1000)

    def test_no_contest_does_not_change_ratings_or_counts(self):
        fights = pd.DataFrame(
            [{"event": "One", "event_date": "2020-01-01", "fighter_1": "Alpha", "fighter_2": "Beta", "result": "NC"}]
        )

        fights_elo, ratings, _peak_elo, _elo_by_search = compute_elo_ratings(fights)
        counts = build_elo_fight_counts(fights_elo)

        self.assertEqual(ratings["Alpha"], 1000)
        self.assertEqual(ratings["Beta"], 1000)
        self.assertEqual(fights_elo.iloc[0]["elo_result_type"], "no_change")
        self.assertNotIn("alpha", counts)

    def test_unknown_result_does_not_change_ratings(self):
        fights = pd.DataFrame(
            [{"event": "One", "event_date": "2020-01-01", "fighter_1": "Alpha", "fighter_2": "Beta", "result": "unknown"}]
        )

        _fights_elo, ratings, _peak_elo, _elo_by_search = compute_elo_ratings(fights)

        self.assertEqual(ratings["Alpha"], 1000)
        self.assertEqual(ratings["Beta"], 1000)

    def test_peak_elo_and_fight_counts_track_completed_fights_only(self):
        fights = pd.DataFrame(
            [
                {"event": "Oldest", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "win"},
                {"event": "Middle", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "draw"},
                {"event": "Newest", "fighter_1": "Alpha Fighter", "fighter_2": "Beta Fighter", "result": "nc"},
            ]
        )

        fights_elo, ratings, peak_elo, _elo_by_search = compute_elo_ratings(fights)
        fight_counts = build_elo_fight_counts(fights_elo)

        self.assertGreaterEqual(peak_elo["Alpha Fighter"], ratings["Alpha Fighter"])
        self.assertEqual(fight_counts["alpha fighter"], 2)
        self.assertEqual(fight_counts["beta fighter"], 2)


if __name__ == "__main__":
    unittest.main()
