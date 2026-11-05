"""Stage 08 learner extension grader. Default targets starter.py.

--reference verifies the grader's solution is correct. Running the default
before implementing the starter is expected to fail.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import shutil
import sqlite3
from tempfile import TemporaryDirectory
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import create_demo_database

LAB = Path(__file__).resolve().parent
TARGET = None


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RegionMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="stage08-region-")
        self.database = Path(self.temp.name) / "fixture.sqlite"
        create_demo_database(self.database)

    def tearDown(self):
        self.temp.cleanup()

    def _insert(self, event_id, magnitude):
        with sqlite3.connect(self.database) as conn:
            conn.execute("""
                INSERT INTO curated_events
                  (event_id, observed_at, source_updated_at, region_code,
                   magnitude, source_sha256, contract_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, "2026-01-03T11:00:00Z", "2026-01-03T11:01:00Z",
                "E", magnitude, "0" * 64, "1.0.0"
            ))

    def test_output_contract(self):
        result = TARGET.region_summary(self.database)
        self.assertEqual(set(result), {"dataset", "items", "limit"})
        self.assertEqual(result["dataset"], "synthetic-training")
        self.assertEqual(result["limit"], 10)

    def test_order_and_total_count(self):
        items = TARGET.region_summary(self.database)["items"]
        self.assertEqual([r["region_code"] for r in items], ["E", "N", "S", "W"])
        self.assertEqual(sum(r["total_events"] for r in items), 4)

    def test_null_magnitude_has_no_mean(self):
        items = TARGET.region_summary(self.database)["items"]
        west = next(r for r in items if r["region_code"] == "W")
        self.assertEqual(west["total_events"], 1)
        self.assertEqual(west["known_magnitude_events"], 0)
        self.assertIsNone(west["average_magnitude"])

    def test_small_limit(self):
        result = TARGET.region_summary(self.database, limit=2)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["limit"], 2)

    def test_invalid_integer_limits(self):
        for value in [0, -1, 21, 1000]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                TARGET.region_summary(self.database, limit=value)

    def test_limit_type_validation(self):
        for value in [True, 1.0, "1", None]:
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                TARGET.region_summary(self.database, limit=value)

    def test_original_database_is_unchanged(self):
        before = digest(self.database)
        TARGET.region_summary(self.database)
        self.assertEqual(digest(self.database), before)

    def test_no_internal_fields_leak(self):
        for row in TARGET.region_summary(self.database)["items"]:
            self.assertEqual(
                set(row),
                {"region_code", "total_events", "known_magnitude_events",
                 "average_magnitude"},
            )

    def test_missing_database_is_never_created(self):
        missing = Path(self.temp.name) / "not-here.sqlite"
        with self.assertRaises((sqlite3.Error, FileNotFoundError, OSError)):
            TARGET.region_summary(missing)
        self.assertFalse(missing.exists())

    def test_grouping_with_null_late_event(self):
        self._insert("newer-null", None)
        east = TARGET.region_summary(self.database, limit=1)["items"][0]
        self.assertEqual(east["region_code"], "E")
        self.assertEqual(east["total_events"], 2)
        self.assertEqual(east["known_magnitude_events"], 1)
        self.assertEqual(east["average_magnitude"], 4.2)

    def test_grouping_with_two_measured_events(self):
        self._insert("newer-measured", 5.8)
        east = TARGET.region_summary(self.database, limit=1)["items"][0]
        self.assertEqual(east["total_events"], 2)
        self.assertEqual(east["known_magnitude_events"], 2)
        self.assertEqual(east["average_magnitude"], 5.0)


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--answers", type=Path, help="Learner answer file (optional)")
    args = parser.parse_args()
    if args.reference and args.answers:
        parser.error("choose --reference or --answers")
    path = (LAB / "instructor/reference.py" if args.reference else
            (args.answers or LAB / "starter.py"))
    if not path.is_file():
        parser.error("answer file not found")
    spec = spec_from_file_location("stage08_region_answer", path)
    TARGET = module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RegionMetricsTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

