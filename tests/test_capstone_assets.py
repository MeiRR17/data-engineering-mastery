"""CI regression for the integrated Stage 13 instructor capstone."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
CAP=ROOT/"capstone"


class CapstoneAssets(unittest.TestCase):
    def test_required_files(self):
        for name in ("instructor/reference.py","starter.py","grade.py",
                     "demo.py","README.md","specification.md"):
            self.assertTrue((CAP/name).is_file(),name)

    def test_starter_is_unimplemented(self):
        self.assertIn("NotImplementedError",(CAP/"starter.py").read_text())

    def test_reference_integration(self):
        check=subprocess.run(
            [sys.executable,str(CAP/"grade.py"),"--reference"],
            capture_output=True,text=True,cwd=ROOT,timeout=50
        )
        self.assertEqual(check.returncode,0,check.stderr+check.stdout)
        self.assertIn("Ran 22 tests",check.stderr)

