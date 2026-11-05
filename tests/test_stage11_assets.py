"""Automatic Stage 11 offline assurance; Kafka broker is a separate optional gate."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"labs/11-streaming"


class Stage11Assets(unittest.TestCase):
    def test_expected_teaching_assets(self):
        for file in ("instructor/reference.py","starter.py","grade.py",
                     "data/synthetic_log.jsonl","README.md","demo.py"):
            self.assertTrue((LAB/file).is_file(),file)

    def test_student_exercise_is_unfinished(self):
        self.assertGreaterEqual(
            (LAB/"starter.py").read_text().count("NotImplementedError"),3)

    def test_offline_reference(self):
        run=subprocess.run(
            [sys.executable,str(LAB/"grade.py"),"--reference"],
            capture_output=True,text=True,timeout=35,cwd=ROOT
        )
        self.assertEqual(run.returncode,0,run.stderr+run.stdout)
        self.assertIn("Ran 25 tests",run.stderr)

