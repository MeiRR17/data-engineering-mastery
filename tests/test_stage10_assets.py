
"""Static + offline reference validation. Real Spark tested in separate CI job."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/10-spark"


class Stage10Assets(unittest.TestCase):
    def test_required_files(self):
        for path in (
            "data/synthetic_events.jsonl",
            "instructor/reference.py", "learner/starter.py",
            "learner/spark_starter.py", "grade.py", "light_cli.py",
            "spark_pipeline.py", "spark_grade.py", "skew_demo.py", "README.md",
        ):
            self.assertTrue((LAB / path).is_file(), path)

    def test_student_paths_start_incomplete(self):
        for path in ("learner/starter.py", "learner/spark_starter.py"):
            self.assertIn("NotImplementedError", (LAB / path).read_text(encoding="utf8"))

    def test_light_reference_oracle(self):
        finished = subprocess.run(
            [sys.executable, str(LAB / "grade.py"), "--reference"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        self.assertEqual(finished.returncode, 0, finished.stdout + "\n" + finished.stderr)
        self.assertIn("Ran 21 tests", finished.stderr)

    def test_light_cli_produces_synthetic_report(self):
        output = subprocess.run(
            [sys.executable, str(LAB / "light_cli.py"), "--partitions", "7"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        self.assertEqual(output.returncode, 0, output.stdout + "\n" + output.stderr)
        self.assertIn('"deduplicated_events": 9', output.stdout)
        self.assertIn('"rejected_rows": 4', output.stdout)
