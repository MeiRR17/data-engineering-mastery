"""Check Stage 09's reference grader and teaching files on ordinary repo CI."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/09-cicd"


class Stage09Assets(unittest.TestCase):
    def test_required_learning_assets(self):
        for file in (
            "instructor/reference.py", "starter.py", "grade.py",
            "demo.py", "README.md",
        ):
            self.assertTrue((LAB / file).is_file(), file)

    def test_starter_is_not_the_reference(self):
        contents = (LAB / "starter.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(contents.count("NotImplementedError"), 5)

    def test_reference_runs_all_security_and_failure_injection_cases(self):
        result = subprocess.run(
            [sys.executable, str(LAB / "grade.py"), "--reference"],
            text=True, capture_output=True, timeout=40, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Ran 26 tests", result.stderr)

