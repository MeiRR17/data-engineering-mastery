"""Offline Stage 07 grader. Student default starts unfinished; --reference verifies oracle."""
import argparse
import copy
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

LAB = Path(__file__).resolve().parent
MODULE = None
NOW = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)


def fixture():
    return json.loads((LAB / "data/synthetic_events.json").read_text(encoding="utf8"))


class DataQualityScenarios(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("pragma foreign_keys=on")
        self.contract = MODULE.load_contract()
        self.rows = fixture()

    def tearDown(self):
        self.db.close()

    def process(self, run_id="batch-1", rows=None, **kwargs):
        return MODULE.process_batch(
            self.db, run_id, self.rows if rows is None else rows, NOW,
            self.contract, **kwargs
        )

    def test_contract_valid_version_and_thresholds(self):
        self.assertEqual(self.contract["schema_version"], "1.0.0")
        self.assertEqual(self.contract["min_valid_ratio"], 0.75)

    def test_contract_rejects_unknown_major_version(self):
        wrong = dict(self.contract, schema_version="2.0.0")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "contract.json"
            path.write_text(json.dumps(wrong), encoding="utf8")
            with self.assertRaises(ValueError):
                MODULE.load_contract(path)

    def test_contract_rejects_invalid_threshold(self):
        wrong = dict(self.contract, max_stale_ratio=1.5)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "contract.json"
            path.write_text(json.dumps(wrong), encoding="utf8")
            with self.assertRaises(ValueError):
                MODULE.load_contract(path)

    def test_clean_batch_publishes_all_four(self):
        r = self.process()
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["published_rows"], 4)
        self.assertEqual(r["magnitude_completeness"], 0.75)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 4)
        self.assertEqual(self.db.execute("select count(*) from lineage_records").fetchone()[0], 4)
        self.assertEqual(self.db.execute("select status from quality_runs").fetchone()[0], "passed")

    def test_duplicate_delivery_quarantined(self):
        batch = copy.deepcopy(self.rows)
        batch.append(copy.deepcopy(batch[0]))
        r = self.process(rows=batch)
        self.assertTrue(r["passed"])
        self.assertEqual((r["total_rows"], r["valid_rows"], r["quarantined_rows"]), (5,4,1))
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "DUPLICATE_EVENT")
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 4)

    def test_missing_required_field_quarantined(self):
        rows = copy.deepcopy(self.rows)
        rows[2].pop("event_id")
        r = self.process(rows=rows)
        self.assertTrue(r["passed"])
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "SCHEMA_MISSING_FIELD")
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 3)

    def test_schema_drift_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["surprise_column"] = "unexpected"
        result = self.process(rows=rows)
        self.assertFalse(result["passed"])  # the remaining 3 rows only have 2 known magnitudes
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "SCHEMA_DRIFT")
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)

    def test_bad_magnitude_never_published(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["magnitude"] = float("inf")
        r = self.process(rows=rows)
        self.assertFalse(r["passed"])
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "BAD_MAGNITUDE")

    def test_naive_timezone_quarantined(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["observed_at"] = "2026-01-03T10:25:00"
        result = self.process(rows=rows)
        self.assertTrue(result["passed"])  # all remaining magnitudes known
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "NAIVE_TIMESTAMP")

    def test_invalid_timestamp_quarantined(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["observed_at"] = "NOT-A-DATE"
        self.process(rows=rows)
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "BAD_TIMESTAMP")

    def test_future_timestamp_quarantined(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["observed_at"] = "2026-01-03T13:00:00Z"
        rows[2]["source_updated_at"] = "2026-01-03T13:01:00Z"
        self.process(rows=rows)
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "FUTURE_TIMESTAMP")

    def test_update_cannot_predate_observation(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["source_updated_at"] = "2026-01-02T10:27:00Z"
        self.process(rows=rows)
        self.assertEqual(self.db.execute(
            "select reason_code from quarantine_records").fetchone()[0], "UPDATE_BEFORE_EVENT")

    def test_quality_gate_blocks_excess_invalid_rows(self):
        rows = copy.deepcopy(self.rows)
        rows[0].pop("event_id")
        rows[1].pop("region_code")
        result = self.process(rows=rows)
        self.assertFalse(result["passed"])
        self.assertIn("VALID_RATIO", result["issues"])
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)
        self.assertEqual(self.db.execute("select count(*) from quarantine_records").fetchone()[0], 2)
        self.assertEqual(self.db.execute("select status from quality_runs").fetchone()[0], "blocked")

    def test_magnitude_completeness_gate(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row["magnitude"] = None
        result = self.process(rows=rows)
        self.assertFalse(result["passed"])
        self.assertIn("COMPLETENESS", result["issues"])
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)

    def test_freshness_gate_blocks_stale_batch(self):
        rows = copy.deepcopy(self.rows)
        for row in rows[:2]:
            row["observed_at"] = "2026-01-01T10:00:00Z"
            row["source_updated_at"] = "2026-01-01T10:02:00Z"
        result = self.process(rows=rows)
        self.assertFalse(result["passed"])
        self.assertEqual(result["stale_rows"], 2)
        self.assertIn("FRESHNESS", result["issues"])
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 0)

    def test_empty_batch_never_published(self):
        result = self.process(rows=[])
        self.assertFalse(result["passed"])
        self.assertIn("EMPTY_BATCH", result["issues"])
        self.assertEqual(result["published_rows"], 0)

    def test_replay_with_new_run_id_is_idempotent(self):
        self.process()
        result = self.process("batch-2")
        self.assertTrue(result["passed"])
        self.assertEqual(result["published_rows"], 0)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 4)
        self.assertEqual(self.db.execute(
            "select sum(was_applied) from lineage_records where run_id='batch-2'").fetchone()[0], 0)

    def test_newer_correction_updates_source_and_lineage(self):
        self.process()
        rows = copy.deepcopy(self.rows)
        rows[0]["magnitude"] = 2.4
        rows[0]["source_updated_at"] = "2026-01-03T11:30:00Z"
        result = self.process("batch-2", rows=rows)
        self.assertEqual(result["published_rows"], 1)
        self.assertEqual(self.db.execute(
            "select magnitude from curated_events where event_id='lab-0701'").fetchone()[0], 2.4)
        self.assertEqual(self.db.execute("select count(*) from curated_events").fetchone()[0], 4)

    def test_old_correction_does_not_replace_newer(self):
        self.process()
        rows = copy.deepcopy(self.rows)
        rows[0]["magnitude"] = 11.0
        rows[0]["source_updated_at"] = "2026-01-03T10:01:00Z"
        result = self.process("batch-2", rows=rows)
        self.assertEqual(result["published_rows"], 0)
        self.assertEqual(self.db.execute(
            "select magnitude from curated_events where event_id='lab-0701'").fetchone()[0], 1.9)

    def test_run_id_is_unique_and_cannot_be_reused(self):
        self.process()
        with self.assertRaises(ValueError):
            self.process("batch-1")
        self.assertEqual(self.db.execute("select count(*) from quality_runs").fetchone()[0], 1)

    def test_simulated_crash_rolls_back_everything(self):
        with self.assertRaises(RuntimeError):
            self.process(simulate_crash=True)
        for table in ("curated_events", "quality_runs", "lineage_records", "quarantine_records"):
            self.assertEqual(self.db.execute(
                "select count(*) from " + table).fetchone()[0], 0)

    def test_quarantine_does_not_store_sensitive_payload(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["private_email"] = "do-not-leak@example.invalid"
        self.process(rows=rows)
        meta = self.db.execute(
            "select reason_code,payload_sha256 from quarantine_records").fetchone()
        self.assertEqual(meta[0], "SCHEMA_DRIFT")
        self.assertEqual(len(meta[1]), 64)
        dump = "\n".join(str(row) for table in ("quarantine_records", "quality_runs")
                         for row in self.db.execute("select * from " + table))
        self.assertNotIn("do-not-leak", dump)

    def test_lineage_graph_is_acyclic_and_connected(self):
        graph = json.loads((LAB / "lineage.json").read_text(encoding="utf8"))
        order = MODULE.lineage_order(graph)
        self.assertEqual(len(order), 5)
        self.assertLess(order.index("source_api"), order.index("daily_metrics"))
        self.assertLess(order.index("contract_validator"), order.index("quarantine"))

    def test_lineage_cycle_is_rejected(self):
        graph = json.loads((LAB / "lineage.json").read_text(encoding="utf8"))
        graph["edges"].append(["daily_metrics", "source_api"])
        with self.assertRaises(ValueError):
            MODULE.lineage_order(graph)

    def test_dangling_lineage_edge_is_rejected(self):
        graph = json.loads((LAB / "lineage.json").read_text(encoding="utf8"))
        graph["edges"].append(["unknown_table", "daily_metrics"])
        with self.assertRaises(ValueError):
            MODULE.lineage_order(graph)

    def test_unconnected_serving_is_rejected(self):
        graph = json.loads((LAB / "lineage.json").read_text(encoding="utf8"))
        graph["edges"] = [e for e in graph["edges"] if e[1] != "daily_metrics"]
        with self.assertRaises(ValueError):
            MODULE.lineage_order(graph)

    def test_contract_rejects_negative_window(self):
        wrong = dict(self.contract, max_freshness_hours=-5)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "contract.json"
            path.write_text(json.dumps(wrong), encoding="utf8")
            with self.assertRaises(ValueError):
                MODULE.load_contract(path)


def main():
    global MODULE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true", help="Grade instructor reference")
    args = parser.parse_args()
    target = LAB / ("instructor/reference.py" if args.reference else "starter.py")
    spec = spec_from_file_location("stage07_target", target)
    MODULE = module_from_spec(spec)
    spec.loader.exec_module(MODULE)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataQualityScenarios)
    results = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if results.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

