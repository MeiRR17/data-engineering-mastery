#!/usr/bin/env python3
"""Stage 02 contract grader. Starter should fail until learner implements it."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SAMPLE = HERE.parents[1] / "projects" / "datapulse" / "data" / "sample.geojson"


def load(path):
    spec = importlib.util.spec_from_file_location("learner_stage02", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def checks(module):
    class Contract(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.features = json.loads(SAMPLE.read_text(encoding="utf-8"))["features"]

        def test_valid_sample_and_null_magnitude(self):
            result = module.clean_batch(copy.deepcopy(self.features))
            self.assertEqual(len(result["valid"]), 3)
            self.assertEqual(result["rejected"], [])
            self.assertEqual(result["valid"][2]["magnitude"], None)
            self.assertEqual(result["valid"][0]["event_id"], "demo-a1")
            self.assertTrue(result["valid"][0]["observed_at"].endswith("+00:00"))

        def test_bad_latitude_is_rejected(self):
            invalid = copy.deepcopy(self.features[0])
            invalid["geometry"]["coordinates"][1] = 91
            result = module.clean_batch([invalid, self.features[1]])
            self.assertEqual(len(result["valid"]), 1)
            self.assertEqual(result["rejected"][0]["index"], 0)
            self.assertTrue(result["rejected"][0]["reason"])

        def test_bool_timestamp_and_nan_rejected(self):
            bad = copy.deepcopy(self.features[0])
            bad["properties"]["time"] = True
            bad2 = copy.deepcopy(self.features[0])
            bad2["properties"]["mag"] = float("nan")
            batch = module.clean_batch([bad, bad2])
            self.assertEqual(len(batch["rejected"]), 2)
            self.assertEqual(batch["valid"], [])

        def test_reject_non_feature_and_updated_before_time(self):
            bad = copy.deepcopy(self.features[0])
            bad["properties"]["updated"] = bad["properties"]["time"] - 1
            result = module.clean_batch([{}, bad])
            self.assertEqual([x["index"] for x in result["rejected"]], [0, 1])

        def test_no_input_mutation(self):
            original = copy.deepcopy(self.features)
            module.clean_batch(self.features)
            self.assertEqual(self.features, original)

        def test_id_boundary_and_wrong_type(self):
            item = copy.deepcopy(self.features[0]); item["id"] = "x" * 65
            other = copy.deepcopy(self.features[0]); other["properties"]["mag"] = "4.2"
            result = module.clean_batch([item, other])
            self.assertEqual(len(result["rejected"]), 2)

    return unittest.defaultTestLoader.loadTestsFromTestCase(Contract)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", action="store_true", help="maintainer check; avoid spoilers while studying")
    args = parser.parse_args()
    mod = load(HERE / ("instructor/reference.py" if args.reference else "starter.py"))
    result = unittest.TextTestRunner(verbosity=2).run(checks(mod))
    raise SystemExit(0 if result.wasSuccessful() else 1)
