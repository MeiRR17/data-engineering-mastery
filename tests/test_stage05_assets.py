"""Offline validation of the Stage 05 teaching and assessment assets."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/05-modeling"


class Stage05Assets(unittest.TestCase):
    def test_all_required_files_are_present(self):
        required = [
            "setup.sql", "starter.sql", "instructor/reference.sql",
            "tests/checks.sql", "tests/source_update.sql", "tests/replay.sql",
            "run_lab.py", "README.md",
        ]
        self.assertTrue(all((LAB / path).is_file() for path in required))

    def test_student_work_is_intentionally_unimplemented(self):
        starter = (LAB / "starter.sql").read_text(encoding="utf8")
        self.assertIn("YOUR EXERCISE", starter)
        self.assertNotIn("insert into analytics.fact_earthquake", starter.lower())

    def test_reference_has_asof_join_replay_and_invoker_view(self):
        reference = (LAB / "instructor/reference.sql").read_text(encoding="utf8").lower()
        for invariant in ["on conflict (event_id)", "valid_from", "valid_to",
                          "security_invoker", "is distinct from"]:
            self.assertIn(invariant, reference)

    def test_private_schema_and_scd2_overlap_guard(self):
        setup = (LAB / "setup.sql").read_text(encoding="utf8").lower()
        for invariant in ["exclude using gist", "btree_gist", "revoke all",
                          "fact_earthquake", "dim_region"]:
            self.assertIn(invariant, setup)


if __name__ == "__main__":
    unittest.main()

