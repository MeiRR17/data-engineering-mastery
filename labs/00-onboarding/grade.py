
"""Stage 00 foundation exercise grader; no network or device inspection."""
import argparse
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

LAB=Path(__file__).resolve().parent
TARGET=None


class FoundationTests(unittest.TestCase):
    def test_minimum_supported_python(self):
        self.assertTrue(TARGET.readiness((3,11,0),True,True)["ready"])

    def test_old_python_reported(self):
        report=TARGET.readiness((3,10,14),True,True)
        self.assertFalse(report["ready"])
        self.assertIn("PYTHON_TOO_OLD",report["issues"])

    def test_git_or_writable_workspace_missing(self):
        report=TARGET.readiness((3,12,0),False,False)
        self.assertEqual(report["issues"],["GIT_UNAVAILABLE","WORKSPACE_READ_ONLY"])

    def test_bad_types_rejected(self):
        for version,git,writable in [(3.12,True,True),((3,12,0),1,True),
                                     ((3,11,0),True,None)]:
            with self.subTest(version=version),self.assertRaises(ValueError):
                TARGET.readiness(version,git,writable)

    def test_no_real_machine_inventory(self):
        self.assertIs(TARGET.readiness((3,12,0),True,True)[
            "real_device_inventory_collected"],False)

    def test_pipeline_order(self):
        graph={"source":[],"validate":["source"],"serve":["curated"],
               "curated":["validate"]}
        self.assertEqual(TARGET.pipeline_order(graph),[
            "source","validate","curated","serve"
        ])

    def test_dangling_graph_edge_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.pipeline_order({"serve":["missing"]})

    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.pipeline_order({"a":["b"],"b":["a"]})

    def test_output_path_inside_workspace(self):
        with TemporaryDirectory(prefix="stage00-") as folder:
            path=TARGET.safe_output_path(folder,"evidence/check.txt")
            self.assertEqual(path,Path(folder)/"evidence/check.txt")
            self.assertFalse(path.exists())

    def test_output_traversal_or_absolute_path_rejected(self):
        with TemporaryDirectory(prefix="stage00-") as folder:
            for bad in ("../private","/etc/passwd","evidence/../../secret"):
                with self.subTest(path=bad),self.assertRaises(ValueError):
                    TARGET.safe_output_path(folder,bad)

    def test_empty_evidence_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.evidence_check({"commit":"x"})

    def test_valid_template_does_not_claim_external_verification(self):
        report=TARGET.evidence_check({
            "commit":"synthetic-sha","command":"python3 -m unittest",
            "test_result":"PASS (synthetic)","reflection":"I can explain the graph"
        })
        self.assertTrue(report["structurally_complete"])
        self.assertFalse(report["independently_verified"])


def main():
    global TARGET
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference",action="store_true")
    args=parser.parse_args()
    path=LAB/("instructor/reference.py" if args.reference else "starter.py")
    spec=spec_from_file_location("stage00_target",path)
    TARGET=module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(FoundationTests))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":
    raise SystemExit(main())
