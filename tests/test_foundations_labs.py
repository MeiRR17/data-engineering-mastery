"""Ensure every reference lab stays runnable and starters remain real exercises."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FoundationsLabTests(unittest.TestCase):
    def run_grade(self, stage, reference=False):
        args = [sys.executable, str(ROOT / "labs" / stage / "grade.py")]
        if reference:
            args.append("--reference")
        return subprocess.run(args, capture_output=True, text=True, timeout=20, cwd=ROOT)

    def test_sql_reference(self):
        run = self.run_grade("01-sql", True)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertIn("4 SQL tasks x 2 datasets", run.stdout)

    def test_python_reference(self):
        run = self.run_grade("02-python", True)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertIn("Ran 6 tests", run.stderr)

    def test_etl_reference(self):
        run = self.run_grade("03-etl", True)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertIn("Ran 7 tests", run.stderr)

    def test_starters_are_real_exercises(self):
        for stage in ("01-sql", "02-python", "03-etl"):
            with self.subTest(stage=stage):
                run = self.run_grade(stage)
                self.assertNotEqual(run.returncode, 0, "Starter incorrectly passes without any learner work")

    def test_readme_link_and_labs_exist(self):
        readme = (ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn("docs/FOUNDATIONS-LABS.md", readme)
        self.assertTrue((ROOT / "docs" / "FOUNDATIONS-LABS.md").is_file())
        for stage in ("01-sql", "02-python", "03-etl"):
            self.assertTrue((ROOT/"labs"/stage/"README.md").is_file())
            self.assertTrue((ROOT/"labs"/stage/"grade.py").is_file())


if __name__ == "__main__":
    unittest.main()
