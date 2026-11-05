
"""Continuously check full 00–13 structural learning coverage."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"scripts/audit_program.py"
spec=spec_from_file_location("dem_program_audit",p)
module=module_from_spec(spec)
spec.loader.exec_module(module)


class TrainingPathStructure(unittest.TestCase):
    def test_fourteen_stages_have_notebooks_and_graders(self):
        result=module.audit()
        self.assertEqual(result["status"],"structure_verified",result["errors"])
        self.assertEqual(result["stages"],14)
        self.assertEqual(result["notebooks"],14)
        self.assertEqual(result["lab_guides"],14)
        self.assertEqual(result["grader_files"],14)

    def test_audit_does_not_claim_external_certification(self):
        result=module.audit()
        text=" ".join(result["external_gates_not_verifiable_by_this_script"])
        self.assertIn("independent learner",text)
        self.assertIn("third-party accreditation",text)
