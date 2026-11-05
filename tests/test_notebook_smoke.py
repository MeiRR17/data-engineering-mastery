
"""Ensure every advanced notebook executes using synthetic stdlib examples."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]


class AdvancedNotebooks(unittest.TestCase):
    def test_advanced_notebook_smoke_run(self):
        result=subprocess.run(
            [sys.executable,str(ROOT/"scripts/notebook_smoke.py")],
            text=True,capture_output=True,cwd=ROOT,timeout=50
        )
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertIn("PASS: 10 offline Stage 04–13 notebooks executed",result.stdout)
