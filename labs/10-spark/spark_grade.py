"""Real PySpark Stage 10 student challenge. --reference verifies instructor job.

Separate from grade.py (light mode); use Java 17 + pyspark==4.0.5.
The Spark session runs only in local[2] mode with synthetic training rows.
"""
import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from instructor.reference import read_jsonl, run_light
from spark_pipeline import normalized_dataframe, result_rows, session

LAB = Path(__file__).resolve().parent
INPUT = LAB / "data/synthetic_events.jsonl"
TARGET = None
SPARK = None


class SparkSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global SPARK
        SPARK = session()

    @classmethod
    def tearDownClass(cls):
        if SPARK:
            SPARK.stop()

    def mart(self, rows, partitions=2):
        df = normalized_dataframe(SPARK, rows)
        return result_rows(TARGET.build_mart(df, partitions))

    def test_reference_fixture_matches_independent_light_oracle(self):
        rows, rejected = read_jsonl(INPUT)
        self.assertEqual(len(rejected), 4)
        self.assertEqual(self.mart(rows), run_light(INPUT)["metrics"])

    def test_different_partition_counts_preserve_results(self):
        rows, _ = read_jsonl(INPUT)
        reference = self.mart(rows, 1)
        self.assertEqual(self.mart(rows, 2), reference)
        self.assertEqual(self.mart(rows, 5), reference)

    def test_reversed_input_is_deterministic(self):
        rows, _ = read_jsonl(INPUT)
        self.assertEqual(self.mart(rows), self.mart(list(reversed(rows)), 3))

    def test_latest_source_revision_wins(self):
        rows, _ = read_jsonl(INPUT)
        b = next(m for m in self.mart(rows) if
                 m["day_utc"] == "2026-01-01" and m["region_code"] == "E")
        self.assertEqual(b["average_magnitude"], 4.4)

    def test_all_null_values_have_null_average(self):
        rows, _ = read_jsonl(INPUT)
        south = next(m for m in self.mart(rows) if m["region_code"] == "S")
        self.assertEqual(south["known_magnitude_events"], 0)
        self.assertIsNone(south["average_magnitude"])

    def test_timezone_offsets_normalized_before_spark(self):
        rows, _ = read_jsonl(INPUT)
        self.assertTrue(any(x["event_id"] == "evt-G"
                            and x["observed_utc"].startswith("2026-01-01")
                            for x in rows))
        self.assertEqual(sum(m["total_events"] for m in self.mart(rows)), 9)

    def test_bad_partition_configuration_rejected(self):
        rows, _ = read_jsonl(INPUT)
        for n in (0, -1, 33, True):
            with self.subTest(partitions=n), self.assertRaises(ValueError):
                TARGET.build_mart(normalized_dataframe(SPARK, rows), n)

    def test_empty_dataframe_yields_empty_mart(self):
        self.assertEqual(self.mart([]), [])

    def test_columns_do_not_expose_lineage_digests(self):
        rows, _ = read_jsonl(INPUT)
        result = TARGET.build_mart(normalized_dataframe(SPARK, rows), 2)
        self.assertEqual(set(result.columns), {
            "day_utc", "region_code", "total_events",
            "known_magnitude_events", "average_magnitude"
        })


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    path = LAB / ("spark_pipeline.py" if args.reference else "learner/spark_starter.py")
    spec = spec_from_file_location("stage10_spark_target", path)
    TARGET = module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SparkSemanticsTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

