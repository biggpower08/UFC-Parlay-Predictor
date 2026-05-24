import unittest

from ufc_predictor.feedback.note_parser import parse_user_notes


class TestNoteParser(unittest.TestCase):
    def test_injury_flag(self):
        flags = parse_user_notes("fighter looked injured before the fight")
        self.assertEqual(flags["injury_flag"], 1)
        self.assertEqual(flags["short_notice_flag"], 0)

    def test_short_notice(self):
        flags = parse_user_notes("short notice replacement")
        self.assertEqual(flags["short_notice_flag"], 1)

    def test_weight_cut(self):
        flags = parse_user_notes("bad weight cut looked drained")
        self.assertEqual(flags["weight_cut_issue_flag"], 1)

    def test_empty_notes(self):
        flags = parse_user_notes("")
        self.assertEqual(sum(flags.values()), 0)


if __name__ == "__main__":
    unittest.main()
