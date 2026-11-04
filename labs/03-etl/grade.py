#!/usr/bin/env python3
"""Stage 03 integration tests with failure injection and replay guarantees."""
import argparse
import copy
import importlib.util
import sqlite3
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(path):
    spec = importlib.util.spec_from_file_location("stage03", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(event_id="e1", magnitude=4.0, updated="2026-11-04T12:01:00Z"):
    return {"event_id": event_id, "observed_at": "2026-11-04T12:00:00Z",
            "source_updated_at": updated, "magnitude": magnitude, "place": "Synthetic Region",
            "latitude": 30.0, "longitude": 35.0}


def checks(module):
    class Contract(unittest.TestCase):
        def setUp(self):
            self.conn = sqlite3.connect(":memory:")
            module.init_db(self.conn)

        def tearDown(self):
            self.conn.close()

        def count(self, table):
            return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

        def test_first_load_and_replay(self):
            first = module.load_batch(self.conn, [event("a"), event("b", 3.0)])
            self.assertEqual(first["written"], 2)
            self.assertEqual(module.load_batch(self.conn, [event("a"), event("b", 3.0)])["written"], 0)
            self.assertEqual(self.count("events"), 2)

        def test_newer_update_and_stale_replay(self):
            module.load_batch(self.conn, [event()])
            fresh = event(magnitude=5.0, updated="2026-11-04T12:02:00Z")
            self.assertEqual(module.load_batch(self.conn, [fresh])["written"], 1)
            module.load_batch(self.conn, [event(magnitude=2.0)])
            self.assertEqual(self.conn.execute("SELECT magnitude FROM events WHERE event_id='e1'").fetchone()[0], 5.0)

        def test_quarantine_no_raw_payload(self):
            bad = event("unsafe")
            bad["latitude"] = 300
            result = module.load_batch(self.conn, [event(), bad])
            self.assertEqual(result["rejected"], 1)
            self.assertEqual(self.count("events"), 1)
            self.assertEqual(self.count("quarantine"), 1)
            module.load_batch(self.conn, [event(), bad])
            self.assertEqual(self.count("quarantine"), 1)
            stored = self.conn.execute("SELECT fingerprint, reason FROM quarantine").fetchone()
            self.assertEqual(len(stored[0]), 64)
            self.assertNotIn("Synthetic Region", stored[1])

        def test_rejection_threshold_is_atomic(self):
            bad1 = event("bad1"); bad1["event_id"] = "bad space"
            bad2 = event("bad2"); bad2["latitude"] = float("nan")
            with self.assertRaises(module.DataQualityError):
                module.load_batch(self.conn, [event(), bad1, bad2], max_reject_fraction=0.5)
            self.assertEqual(self.count("events"), 0)
            self.assertEqual(self.count("quarantine"), 0)

        def test_mid_batch_crash_rolls_back(self):
            with self.assertRaises(RuntimeError):
                module.load_batch(self.conn, [event("x"), event("y")], fail_after=0)
            self.assertEqual(self.count("events"), 0)
            self.assertEqual(self.count("quarantine"), 0)

        def test_invalid_timestamps_and_bool(self):
            bad = event("t"); bad["source_updated_at"] = "2026-11-04T13:00:00"  # naive
            bad2 = event("b"); bad2["magnitude"] = True
            result = module.load_batch(self.conn, [bad, bad2], max_reject_fraction=1.0)
            self.assertEqual(result["rejected"], 2)
            self.assertEqual(self.count("events"), 0)

        def test_empty_batch_and_invalid_threshold(self):
            self.assertEqual(module.load_batch(self.conn, []), {"written":0,"rejected":0,"unchanged":0})
            with self.assertRaises(ValueError):
                module.load_batch(self.conn, [event()], max_reject_fraction=1.5)

    return unittest.defaultTestLoader.loadTestsFromTestCase(Contract)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", action="store_true")
    args = ap.parse_args()
    module = load(HERE / ("instructor/reference.py" if args.reference else "starter.py"))
    result = unittest.TextTestRunner(verbosity=2).run(checks(module))
    raise SystemExit(0 if result.wasSuccessful() else 1)
