"""Offline proof that Stage 06 reference grader is usable and starter is intentionally incomplete."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Stage06RepositoryTests(unittest.TestCase):
    def test_reference_grader(self):
        command = [sys.executable, str(ROOT/"labs/06-orchestration/grade.py"), "--reference"]
        result = subprocess.run(command, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Ran 17 tests", result.stderr)

    def test_student_exercise_starts_as_todo(self):
        data = (ROOT/"labs/06-orchestration/starter.py").read_text(encoding="utf8")
        self.assertIn('NotImplementedError', data)
        self.assertIn('ingest_day', data)
