import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from datapulse.etl import DataQualityError, normalize, transform_feed
from datapulse.ingest import run


class TransformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = json.loads((ROOT / "data" / "sample.geojson").read_text())

    def test_three_rows_and_nullable_magnitude(self):
        rows, rejects = transform_feed(self.feed)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rejects, [])
        self.assertIsNone(rows[2]["magnitude"])

    def test_stable_checksum(self):
        feature = self.feed["features"][0]
        self.assertEqual(normalize(feature)["payload_sha256"], normalize(copy.deepcopy(feature))["payload_sha256"])

    def test_invalid_latitude_is_rejected(self):
        feed = copy.deepcopy(self.feed)
        feed["features"][0]["geometry"]["coordinates"][1] = 95
        rows, rejects = transform_feed(feed)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rejects[0]["reason"], "latitude out of range")

    def test_deduplicates_on_latest_source_update(self):
        feed = copy.deepcopy(self.feed)
        older = copy.deepcopy(feed["features"][0])
        older["properties"]["updated"] -= 1000
        feed["features"].append(older)
        rows, rejects = transform_feed(feed)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rejects, [])

    def test_reject_rate_guardrail(self):
        feed = copy.deepcopy(self.feed)
        feed["features"][0]["geometry"]["coordinates"][1] = 95
        with self.assertRaisesRegex(DataQualityError, "reject rate"):
            run(feed)

    def test_end_to_end_dry_run(self):
        outcome = run(self.feed)
        self.assertEqual(outcome["source_rows"], 3)
        self.assertEqual(outcome["valid_rows"], 3)
        self.assertEqual(outcome["loaded_rows"], 0)


if __name__ == "__main__":
    unittest.main()
