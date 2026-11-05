"""Offline validation of teaching assets; reference grader runs without cloud."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/07-quality"


class Stage07AssetsTests(unittest.TestCase):
    def test_contract_and_lineage_fixtures_exist(self):
        for name in (
            "contract.json", "lineage.json", "data/synthetic_events.json",
            "starter.py", "instructor/reference.py", "grade.py", "README.md",
        ):
            self.assertTrue((LAB / name).is_file(), name)

    def test_student_starter_is_unfinished(self):
        source = (LAB / "starter.py").read_text(encoding="utf8")
        self.assertGreaterEqual(source.count("NotImplementedError"), 5)

    def test_reference_grader_all_pass(self):
        result = subprocess.run(
            [sys.executable, str(LAB / "grade.py"), "--reference"],
            text=True, capture_output=True, timeout=40
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Ran 27 tests", result.stderr)

