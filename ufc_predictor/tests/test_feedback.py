import tempfile
import unittest
from pathlib import Path

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.feedback import feedback_handler


class TestFeedback(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig = settings.FEEDBACK_LOG_CSV
        settings.FEEDBACK_LOG_CSV = Path(self._tmpdir.name) / "feedback_log.csv"

    def tearDown(self):
        settings.FEEDBACK_LOG_CSV = self._orig
        self._tmpdir.cleanup()

    def test_save_and_load(self):
        row = feedback_handler.save_feedback(
            {
                "fighter_a": "Jon Jones",
                "fighter_b": "Stipe Miocic",
                "predicted_winner": "Jon Jones",
                "actual_winner": "Stipe Miocic",
                "confidence": 0.65,
                "was_correct": False,
                "user_notes": "injured leg",
            }
        )
        df = feedback_handler.load_feedback()
        self.assertEqual(len(df), 1)
        self.assertEqual(row["fighter_a"], "Jon Jones")
        self.assertIn("prediction_id", row)


if __name__ == "__main__":
    unittest.main()
