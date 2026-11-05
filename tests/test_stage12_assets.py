"""Offline Stage 12 repository teaching and grader gate."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"labs/12-reliability"


class Stage12Assets(unittest.TestCase):
    def test_files_present(self):
        for name in ("instructor/reference.py","starter.py","grade.py",
                     "README.md","incident_drill.py","policy.json"):
            self.assertTrue((LAB/name).exists(),name)

    def test_reference_passes(self):
        result=subprocess.run(
            [sys.executable,str(LAB/"grade.py"),"--reference"],
            cwd=ROOT,capture_output=True,text=True,timeout=40
        )
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn("Ran 27 tests",result.stderr)

    def test_learner_starter_unfinished(self):
        self.assertGreaterEqual((LAB/"starter.py").read_text().count("NotImplementedError"),6)

