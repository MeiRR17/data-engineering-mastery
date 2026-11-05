
"""Stage 00 reference and asset sanity checks."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"labs/00-onboarding"

class Stage00Assets(unittest.TestCase):
    def test_required(self):
        for p in ("README.md","grade.py","starter.py","instructor/reference.py"):
            self.assertTrue((LAB/p).is_file(),p)

    def test_reference_suite(self):
        run=subprocess.run(
            [sys.executable,str(LAB/"grade.py"),"--reference"],
            cwd=ROOT,text=True,capture_output=True,timeout=25
        )
        self.assertEqual(run.returncode,0,run.stderr+run.stdout)
        self.assertIn("Ran 12 tests",run.stderr)

    def test_student_starter_incomplete(self):
        self.assertIn("NotImplementedError",(LAB/"starter.py").read_text())
