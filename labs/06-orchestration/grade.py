"""Stage 06 grader. Default grades learner starter, --reference validates the test oracle."""
import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parent
MODULE = None


def source_for(day="2026-01-01", updated=1, magnitude=3.0, event_id="evt-1"):
    return [{"event_id": event_id, "event_day": day,
             "source_updated": updated, "magnitude": magnitude}]


class Stage06Tests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")

    def tearDown(self):
        self.db.close()

    def test_dag_topological_order(self):
        dag = {"publish": ("load",), "load": ("validate",),
               "validate": ("extract",), "extract": ()}
        self.assertEqual(MODULE.dag_order(dag),
                         ["extract", "validate", "load", "publish"])

    def test_independent_tasks_sorted_deterministically(self):
        self.assertEqual(MODULE.dag_order({"z": (), "a": ()}), ["a", "z"])

    def test_dag_rejects_cycles(self):
        with self.assertRaises(ValueError):
            MODULE.dag_order({"a": ("b",), "b": ("a",)})

    def test_dag_rejects_dangling_dependencies(self):
        with self.assertRaises(ValueError):
            MODULE.dag_order({"load": ("missing",)})

    def test_inclusive_backfill(self):
        self.assertEqual(MODULE.backfill_days("2026-01-01", "2026-01-03"),
                         ["2026-01-01", "2026-01-02", "2026-01-03"])

    def test_invalid_backfill_ranges_fail_closed(self):
        for start, end in [("2026-02-01","2026-01-01"),
                           ("2026-01-01","2026-02-15"),
                           ("hello","2026-01-02")]:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                MODULE.backfill_days(start, end)

    def test_success_and_checkpoint(self):
        result = MODULE.ingest_day(self.db, "2026-01-01", lambda day: source_for(day))
        self.assertEqual((result["status"], result["attempts"]), ("success", 1))
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 1)
        journal = self.db.execute(
            "select status,attempts,submitted_rows from pipeline_runs").fetchone()
        self.assertEqual(journal, ("success",1,1))

    def test_successful_window_is_not_refetched(self):
        MODULE.ingest_day(self.db, "2026-01-01", lambda day: source_for(day))
        def unexpected(day):
            raise AssertionError("completed window was fetched again")
        self.assertEqual(MODULE.ingest_day(self.db, "2026-01-01", unexpected)["status"],
                         "skipped")

    def test_transient_failure_retries_with_bound(self):
        calls = []
        def flaky(day):
            calls.append(day)
            if len(calls) <= 2:
                raise MODULE.TransientSourceError("temporary 503")
            return source_for(day)
        output = MODULE.ingest_day(self.db, "2026-01-01", flaky, attempts=3)
        self.assertEqual(output["attempts"], 3)
        self.assertEqual(len(calls), 3)

    def test_transient_exhausted_and_failure_journal(self):
        count = []
        def unavailable(day):
            count.append(day)
            raise MODULE.TransientSourceError("still unavailable")
        with self.assertRaises(MODULE.TransientSourceError):
            MODULE.ingest_day(self.db, "2026-01-01", unavailable, attempts=2)
        self.assertEqual(len(count), 2)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)
        self.assertEqual(self.db.execute("select status from pipeline_runs").fetchone()[0],
                         "failed")

    def test_bad_second_row_rolls_back_first(self):
        def broken(day):
            return source_for(day) + source_for(day, event_id="bad", magnitude=99)
        with self.assertRaises(ValueError):
            MODULE.ingest_day(self.db, "2026-01-01", broken)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)
        self.assertEqual(self.db.execute("select status from pipeline_runs").fetchone()[0],
                         "failed")

    def test_commit_before_lost_ack_replay(self):
        with self.assertRaises(MODULE.AcknowledgementLost):
            MODULE.ingest_day(self.db, "2026-01-01", lambda day: source_for(day),
                              lose_ack=True)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 1)
        self.assertEqual(MODULE.ingest_day(self.db, "2026-01-01",
                         lambda day: source_for(day))["status"], "skipped")
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 1)

    def test_force_backfill_updates_newer_event(self):
        day = "2026-01-01"
        MODULE.ingest_day(self.db, day, lambda d: source_for(d, updated=1, magnitude=2.0))
        MODULE.ingest_day(self.db, day,
                          lambda d: source_for(d, updated=2, magnitude=4.0), force=True)
        self.assertEqual(self.db.execute("select magnitude from curated_events").fetchone()[0],4.0)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0],1)

    def test_stale_source_cannot_overwrite_fresher_event(self):
        day = "2026-01-01"
        MODULE.ingest_day(self.db, day,lambda d:source_for(d,updated=9,magnitude=4.5))
        MODULE.ingest_day(self.db, day,lambda d:source_for(d,updated=1,magnitude=8.0),force=True)
        self.assertEqual(self.db.execute("select magnitude from curated_events").fetchone()[0],4.5)

    def test_out_of_order_duplicate_in_single_batch(self):
        day = "2026-01-01"
        MODULE.ingest_day(self.db, day,
                          lambda d:source_for(d,updated=3,magnitude=5.5)
                                 +source_for(d,updated=2,magnitude=1.0))
        self.assertEqual(self.db.execute("select magnitude from curated_events").fetchone()[0],5.5)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0],1)

    def test_backfill_processes_independent_days(self):
        for day in MODULE.backfill_days("2026-01-01","2026-01-03"):
            MODULE.ingest_day(self.db,day,lambda d:source_for(d,event_id=d))
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0],3)
        self.assertEqual(self.db.execute("select count(*) from pipeline_runs").fetchone()[0],3)

    def test_invalid_retry_config_rejected(self):
        for attempts in [0, -1, 11, True]:
            with self.subTest(attempts=attempts), self.assertRaises(ValueError):
                MODULE.ingest_day(self.db, "2026-01-01",
                                  lambda d:source_for(d), attempts=attempts)


def main():
    global MODULE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true",
                        help="Test the instructor's trusted baseline")
    args = parser.parse_args()
    path = (ROOT/"instructor"/"reference.py" if args.reference else ROOT/"starter.py")
    spec = spec_from_file_location("stage06_target", path)
    MODULE = module_from_spec(spec)
    spec.loader.exec_module(MODULE)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Stage06Tests))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
