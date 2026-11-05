"""Offline assurance; real Postgres integration runs in a separate CI job."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/04-postgres"

class Stage04Assets(unittest.TestCase):
    def test_required_files_parse(self):
        for name in ("run_lab.py", "bootstrap.sql", "seed.sql", "starter.sql",
                     "instructor/reference.sql", "tests/checks.sql", "README.md"):
            self.assertTrue((LAB/name).is_file(), name)
        ast.parse((LAB/"run_lab.py").read_text(encoding="utf8"))

    def test_student_starter_unfinished(self):
        student = (LAB/"starter.sql").read_text(encoding="utf8").lower()
        instructor = (LAB/"instructor/reference.sql").read_text(encoding="utf8").lower()
        self.assertNotIn("create or replace view", student)
        self.assertIn("security_invoker = true", instructor)
        self.assertIn("revoke all", instructor)
        self.assertIn("grant select", instructor)

    def test_runner_is_disposable(self):
        code = (LAB/"run_lab.py").read_text(encoding="utf8")
        self.assertIn("uuid.uuid4", code)
        self.assertIn("finally:", code)
        self.assertNotIn("supabase db push", code)
        self.assertNotIn("docker system prune", code)

    def test_canonical_schema_security(self):
        sql = (ROOT/"projects/datapulse/database/001_init.sql").read_text(encoding="utf8").lower()
        for phrase in ("enable row level security", "security_invoker = true",
                       "revoke all on function", "on conflict"):
            self.assertIn(phrase, sql)

if __name__ == "__main__":
    unittest.main()
