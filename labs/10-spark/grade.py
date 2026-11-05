"""Stage 10 light-mode learner grader (stdlib, offline).

Default: tests learner/starter.py (unfinished by design).
--reference: tests instructor reference and the independent fixture oracle.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

LAB = Path(__file__).resolve().parent
TARGET = None
FIXTURE = LAB / "data/synthetic_events.jsonl"


def row(event_id="A", observed_at="2026-01-01T10:00:00Z",
        source_updated_at="2026-01-01T10:10:00Z", region_code="N", magnitude=2.0):
    return {
        "event_id": event_id, "observed_at": observed_at,
        "source_updated_at": source_updated_at, "region_code": region_code,
        "magnitude": magnitude,
    }


class DistributedSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="stage10-tests-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "events.jsonl"

    def run_rows(self, rows, partitions=2):
        self.path.write_text("\n".join(json.dumps(r, allow_nan=True) for r in rows) + "\n")
        return TARGET.run_light(self.path, partitions=partitions)

    def test_reference_fixture_top_level_counts(self):
        result = TARGET.run_light(FIXTURE)
        counts = (result["input_rows"], result["valid_rows"], result["rejected_rows"],
                  result["deduplicated_events"], result["duplicates_removed"])
        self.assertEqual(counts, (16, 12, 4, 9, 3))

    def test_reference_fixture_rejected_reasons(self):
        result = TARGET.run_light(FIXTURE)
        self.assertEqual(result["rejected_reasons"], [
            "BAD_MAGNITUDE", "BAD_REGION", "NAIVE_TIMESTAMP", "SCHEMA_DRIFT"
        ])

    def test_reference_fixture_metrics_are_exhaustive(self):
        result = TARGET.run_light(FIXTURE)
        expected = [
            ("2026-01-01", "E", 2, 1, 4.4),
            ("2026-01-01", "N", 2, 2, 2.25),
            ("2026-01-02", "E", 1, 1, 5.7),
            ("2026-01-02", "N", 1, 1, 2.2),
            ("2026-01-02", "W", 2, 1, 0.6),
            ("2026-01-03", "S", 1, 0, None),
        ]
        self.assertEqual([
            (r["day_utc"], r["region_code"], r["total_events"],
             r["known_magnitude_events"], r["average_magnitude"])
            for r in result["metrics"]
        ], expected)

    def test_one_two_and_seven_partitions_match(self):
        outputs = [TARGET.run_light(FIXTURE, partitions=n) for n in (1, 2, 7)]
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])

    def test_shuffled_input_preserves_result(self):
        rows = [json.loads(x) for x in FIXTURE.read_text().splitlines()]
        original = self.run_rows(rows)
        reversed_result = self.run_rows(list(reversed(rows)))
        self.assertEqual(original["metrics"], reversed_result["metrics"])

    def test_partition_boundaries_are_validated(self):
        for bad in (0, -1, 33, 1.5, True, "2"):
            with self.subTest(partitions=bad), self.assertRaises(ValueError):
                TARGET.run_light(FIXTURE, partitions=bad)

    def test_missing_file_is_not_created(self):
        missing = Path(self.temp.name) / "does-not-exist.jsonl"
        with self.assertRaises((FileNotFoundError, OSError)):
            TARGET.run_light(missing)
        self.assertFalse(missing.exists())

    def test_empty_file_has_no_metrics(self):
        self.path.write_text("")
        result = TARGET.run_light(self.path)
        self.assertEqual(result["input_rows"], 0)
        self.assertEqual(result["metrics"], [])
        self.assertEqual(result["deduplicated_events"], 0)

    def test_latest_update_wins_not_highest_measurement(self):
        older = row(event_id="B", magnitude=9.0)
        newer = row(event_id="B", magnitude=2.0,
                    source_updated_at="2026-01-02T10:10:00Z")
        result = self.run_rows([newer, older])
        self.assertEqual(result["duplicates_removed"], 1)
        self.assertEqual(result["metrics"][0]["average_magnitude"], 2.0)

    def test_same_timestamp_conflict_has_stable_result(self):
        a = row(event_id="X", magnitude=1.0)
        b = row(event_id="X", magnitude=3.0)
        first = self.run_rows([a, b], partitions=1)
        second = self.run_rows([b, a], partitions=5)
        self.assertEqual(first, second)
        self.assertEqual(first["deduplicated_events"], 1)

    def test_null_is_excluded_from_average(self):
        result = self.run_rows([row("A", magnitude=None),
                                row("B", magnitude=4.0)])
        self.assertEqual(result["metrics"][0]["total_events"], 2)
        self.assertEqual(result["metrics"][0]["known_magnitude_events"], 1)
        self.assertEqual(result["metrics"][0]["average_magnitude"], 4.0)

    def test_all_null_has_null_mean(self):
        result = self.run_rows([row("A", magnitude=None)])
        self.assertIsNone(result["metrics"][0]["average_magnitude"])

    def test_timezone_conversion_affects_utc_day(self):
        result = self.run_rows([row("A", observed_at="2026-01-02T00:30:00+02:00",
                                    source_updated_at="2026-01-02T00:35:00+02:00")])
        self.assertEqual(result["metrics"][0]["day_utc"], "2026-01-01")

    def test_naive_timestamp_is_quarantined(self):
        result = self.run_rows([row(observed_at="2026-01-01T10:00:00")])
        self.assertEqual(result["rejected_reasons"], ["NAIVE_TIMESTAMP"])
        self.assertEqual(result["metrics"], [])

    def test_bad_json_is_quarantined(self):
        self.path.write_text("{broken json}\n")
        result = TARGET.run_light(self.path)
        self.assertEqual(result["rejected_reasons"], ["BAD_JSON"])
        self.assertEqual(result["input_rows"], 1)

    def test_magnitude_boolean_and_out_of_range_are_rejected(self):
        result = self.run_rows([row("B", magnitude=True),
                                row("C", magnitude=13.0)])
        self.assertEqual(result["rejected_reasons"], ["BAD_MAGNITUDE", "BAD_MAGNITUDE"])
        self.assertEqual(result["deduplicated_events"], 0)

    def test_missing_and_extra_schema_fields_are_rejected(self):
        a, b = row("A"), row("B")
        del a["event_id"]
        b["private_email"] = "do-not-log@example.invalid"
        result = self.run_rows([a, b])
        self.assertEqual(result["rejected_reasons"], ["SCHEMA_DRIFT", "SCHEMA_DRIFT"])
        self.assertNotIn("private_email", json.dumps(result))

    def test_invalid_region_and_id_are_quarantined(self):
        result = self.run_rows([row("A", region_code="e"),
                                row("bad space")])
        self.assertEqual(result["rejected_reasons"], ["BAD_ID", "BAD_REGION"])

    def test_source_update_cannot_predate_observation(self):
        result = self.run_rows([row(source_updated_at="2025-12-31T23:00:00Z")])
        self.assertEqual(result["rejected_reasons"], ["UPDATE_BEFORE_OBSERVATION"])

    def test_group_keys_do_not_mix_regions(self):
        result = self.run_rows([row("A", region_code="E", magnitude=1.0),
                                row("B", region_code="N", magnitude=5.0)])
        self.assertEqual(len(result["metrics"]), 2)
        self.assertEqual(sum(x["total_events"] for x in result["metrics"]), 2)

    def test_no_identifying_raw_data_in_report(self):
        result = self.run_rows([row("A"), {"private_token": "DO_NOT_ECHO"}])
        text = json.dumps(result)
        self.assertNotIn("DO_NOT_ECHO", text)
        self.assertNotIn("private_token", text)


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    target = LAB / ("instructor/reference.py" if args.reference else "learner/starter.py")
    spec = spec_from_file_location("stage10_target", target)
    TARGET = module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(DistributedSemanticsTests)
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

