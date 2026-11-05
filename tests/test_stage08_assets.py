"""Verify the real Stage 08 read-only API regression suite in ordinary repo CI."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/08-serving"


class Stage08Assets(unittest.TestCase):
    def test_all_assets_present(self):
        for name in ("service.py", "demo.py", "serve.py", "grade.py",
                     "web/index.html", "web/styles.css", "web/app.js",
                     "README.md"):
            self.assertTrue((LAB / name).is_file(), name)

    def test_http_service_regressions_pass(self):
        result = subprocess.run(
            [sys.executable, str(LAB / "grade.py")],
            capture_output=True, text=True, timeout=45,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Ran 24 tests", result.stderr)

