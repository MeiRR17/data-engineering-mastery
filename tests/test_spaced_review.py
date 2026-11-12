"""Offline spaced-review contract, including negative and privacy cases."""
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import spaced_review as review


class SpacedReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_path = Path(self.tmp.name) / "learner" / "reviews.local.json"
        self.day = date(2026, 11, 12)
        self.stages = {"00", "01", "07"}
        self.state = review.load_state(self.state_path)

    def test_missing_state_is_empty_and_read_only(self):
        self.assertEqual(self.state, {"schema_version": 1, "cards": {}})
        self.assertFalse(self.state_path.exists())

    def test_stage_validation_and_duplicates(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            review.add_stage(self.state, "88", self.day, self.stages)
        review.add_stage(self.state, "07", self.day, self.stages)
        with self.assertRaisesRegex(ValueError, "already scheduled"):
            review.add_stage(self.state, "07", self.day, self.stages)
        self.assertEqual(len(self.state["cards"]), 1)

    def test_good_schedule_progresses_1_3_7_days(self):
        review.add_stage(self.state, "07", self.day, self.stages)
        for shift, interval in [(0, 1), (1, 3), (4, 7)]:
            now = self.day + timedelta(days=shift)
            review.record_review(self.state, "07", "good", now)
            self.assertEqual(self.state["cards"]["07"]["due"], (now + timedelta(days=interval)).isoformat())
        self.assertEqual(self.state["cards"]["07"]["count"], 3)

    def test_again_resets_and_easy_advances(self):
        review.add_stage(self.state, "01", self.day, self.stages)
        review.record_review(self.state, "01", "easy", self.day)
        self.assertEqual(self.state["cards"]["01"]["due"], (self.day + timedelta(days=3)).isoformat())
        review.record_review(self.state, "01", "again", self.day + timedelta(days=3))
        self.assertEqual(self.state["cards"]["01"]["step"], 0)
        self.assertEqual(self.state["cards"]["01"]["due"], (self.day + timedelta(days=4)).isoformat())

    def test_repeated_or_backdated_review_is_rejected(self):
        review.add_stage(self.state, "07", self.day, self.stages)
        review.record_review(self.state, "07", "hard", self.day)
        for day in (self.day, self.day - timedelta(days=1)):
            with self.assertRaisesRegex(ValueError, "one review"):
                review.record_review(self.state, "07", "good", day)
        self.assertEqual(self.state["cards"]["07"]["count"], 1)

    def test_due_reports_overdue_deterministically(self):
        review.add_stage(self.state, "01", self.day, self.stages)
        review.add_stage(self.state, "07", self.day + timedelta(days=2), self.stages)
        self.assertEqual(review.due_stages(self.state, self.day + timedelta(days=1)), [("01", 1)])
        text = review.show_status(self.state, self.day + timedelta(days=1), True)
        self.assertIn("01  1d overdue", text)
        self.assertIn("07  upcoming 2026-11-14", text)

    def test_invalid_json_not_overwritten(self):
        self.state_path.parent.mkdir(parents=True)
        self.state_path.write_text('{"schema_version": 1, "cards": []}')
        before = self.state_path.read_bytes()
        with self.assertRaisesRegex(ValueError, "schema"):
            review.load_state(self.state_path)
        self.assertEqual(before, self.state_path.read_bytes())

    def test_local_atomic_persistence_has_no_personal_identifiers(self):
        review.add_stage(self.state, "00", self.day, self.stages)
        review.save_state(self.state, self.state_path)
        saved = self.state_path.read_text()
        self.assertEqual(json.loads(saved), review.load_state(self.state_path))
        self.assertNotIn("alias", saved)
        self.assertNotIn("answer", saved)
        self.assertNotIn("email", saved)
        if sys.platform != "win32":
            self.assertEqual(self.state_path.stat().st_mode & 0o777, 0o600)

    def test_symlink_refused(self):
        target = Path(self.tmp.name) / "target.json"
        target.write_text("private")
        self.state_path.parent.mkdir(parents=True)
        try:
            self.state_path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "symlink"):
            review.load_state(self.state_path)
        with self.assertRaisesRegex(ValueError, "symlink"):
            review.save_state(self.state, self.state_path)
        self.assertEqual(target.read_text(), "private")

    def test_dates_and_untracked_state_location(self):
        for invalid in ("2026-02-30", "12/11/2026", "20261112", "tomorrow"):
            with self.assertRaises(ValueError):
                review.parse_day(invalid)
        self.assertEqual(review.STATE.name, "reviews.local.json")
        ignore = (ROOT / ".gitignore").read_text()
        self.assertIn("learner/*.local.json", ignore)


if __name__ == "__main__":
    unittest.main()
