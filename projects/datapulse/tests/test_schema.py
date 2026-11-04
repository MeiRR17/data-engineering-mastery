import unittest
from pathlib import Path

SQL = (Path(__file__).resolve().parents[1] / "database" / "001_init.sql").read_text()


class SecurityReviewAssertions(unittest.TestCase):
    def test_rls_all_exposed_tables(self):
        for table in ("raw_earthquakes", "earthquakes", "ingest_runs"):
            self.assertIn(f"alter table public.{table} enable row level security", SQL)

    def test_public_read_is_curated_only(self):
        self.assertIn("grant select on public.earthquakes to anon", SQL)
        self.assertIn("revoke all on public.raw_earthquakes from anon, authenticated", SQL)
        self.assertIn("revoke all on public.ingest_runs from anon, authenticated", SQL)
        self.assertIn("security_invoker = true", SQL)

    def test_ingest_rpc_not_public_executable(self):
        self.assertIn("security invoker", SQL)
        self.assertIn("revoke all on function public.ingest_earthquake_batch(jsonb) from public, anon, authenticated", SQL)


if __name__ == "__main__":
    unittest.main()
