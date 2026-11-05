"""Assessment cannot issue credentials; it only verifies evidence structure."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1]


def load(path,name):
    spec=spec_from_file_location(name,ROOT/path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(prefix="dem-assessment-tests-")
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)
        self.evaluator=load(Path("assessment/evaluate.py"),"dem_evaluate")
        self.exam=load(Path("assessment/generate_transfer.py"),"dem_transfer")

    def submission(self,ready=False):
        template=json.loads((ROOT/"assessment/submission.example.json").read_text())
        template["candidate_alias"]="Test Student — synthetic"
        if ready:
            for id,entry in template["stages"].items():
                entry["scores"]={key:3 for key in entry["scores"]}
                entry["independent_transfer"]=True
                for ref in entry["evidence"]:
                    path=self.dir/ref
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_text("Synthetic test evidence for "+id)
            template["final_exam"]={
                "independent_implementation":32,
                "incident":16,"system_design":16,"defense":16
            }
            template["reviewer"]={
                "name":"Synthetic Reviewer",
                "independent_review_completed":True,
                "capstone_demonstrated":True
            }
            template["external_claims"]={
                "cloud_deployed":False,
                "kafka_broker_run":True,"spark_runtime_run":True
            }
        path=self.dir/"submission.json"
        path.write_text(json.dumps(template),encoding="utf8")
        return path

    def test_incomplete_example_never_claims_completion(self):
        result=self.evaluator.evaluate(self.submission())
        self.assertEqual(result["status"],"needs_evidence")
        self.assertEqual(result["stages_with_structurally_valid_evidence"],0)

    def test_all_structural_evidence_only_advances_to_human_review(self):
        result=self.evaluator.evaluate(self.submission(True))
        self.assertEqual(result["status"],"ready_for_human_review")
        self.assertEqual(result["stages_with_structurally_valid_evidence"],14)
        self.assertEqual(result["exam_score_self_reported"],80)
        self.assertIn("No certificate issued",result["caveat"])

    def test_missing_stage_blocks_completion(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        del entry["stages"]["12"]
        path.write_text(json.dumps(entry))
        result=self.evaluator.evaluate(path)
        self.assertEqual(result["status"],"needs_evidence")
        self.assertIn("exactly 14 stages", " ".join(result["issues"]))

    def test_boolean_rubric_score_not_accepted(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["stages"]["02"]["scores"]["concepts"]=True
        path.write_text(json.dumps(entry))
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_evidence_outside_workspace_rejected(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["stages"]["01"]["evidence"][0]="../../private.txt"
        path.write_text(json.dumps(entry))
        result=self.evaluator.evaluate(path)
        self.assertEqual(result["status"],"needs_evidence")

    def test_empty_evidence_rejected(self):
        path=self.submission(True)
        target=self.dir/"evidence/03-tests.txt"
        target.write_text("")
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_unresolved_critical_finding_blocks(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["stages"]["08"]["critical_findings"]=["P0: exposed secrets"]
        path.write_text(json.dumps(entry))
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_independent_transfer_required(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["stages"]["09"]["independent_transfer"]=False
        path.write_text(json.dumps(entry))
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_exam_section_minima_required_even_with_high_total(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["final_exam"]["incident"]=0
        entry["final_exam"]["independent_implementation"]=40
        entry["final_exam"]["defense"]=20
        entry["final_exam"]["system_design"]=20
        path.write_text(json.dumps(entry))
        result=self.evaluator.evaluate(path)
        self.assertEqual(result["status"],"needs_evidence")
        self.assertIn("incident below section minimum"," ".join(result["issues"]))

    def test_missing_reviewer_blocks(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["reviewer"]["independent_review_completed"]=False
        path.write_text(json.dumps(entry))
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_full_mode_evidence_is_not_optional_for_full_claim(self):
        path=self.submission(True)
        entry=json.loads(path.read_text())
        entry["external_claims"]["kafka_broker_run"]=False
        path.write_text(json.dumps(entry))
        self.assertEqual(self.evaluator.evaluate(path)["status"],"needs_evidence")

    def test_exam_generator_separates_candidate_and_reviewer(self):
        output=self.dir/"exam"
        self.exam.generate(1542,output)
        self.assertTrue((output/"candidate/events.jsonl").is_file())
        self.assertTrue((output/"reviewer_only/answer_key.json").is_file())
        candidate_text="\n".join(p.read_text() for p in
            (output/"candidate").rglob("*") if p.is_file())
        self.assertNotIn('"regional_average"',candidate_text)

    def test_exam_generator_deterministic_by_seed(self):
        a,b=self.dir/"exam-a",self.dir/"exam-b"
        self.exam.generate(12345,a)
        self.exam.generate(12345,b)
        self.assertEqual(
            (a/"candidate/events.jsonl").read_bytes(),
            (b/"candidate/events.jsonl").read_bytes()
        )
        self.assertEqual(
            (a/"reviewer_only/answer_key.json").read_bytes(),
            (b/"reviewer_only/answer_key.json").read_bytes()
        )

    def test_exam_generator_refuses_overwrite(self):
        a=self.dir/"exam"
        self.exam.generate(88,a)
        with self.assertRaises(FileExistsError):
            self.exam.generate(89,a)

    def test_exam_generator_refuses_bad_seed(self):
        for seed in (-1,0,True,2**70):
            with self.subTest(seed=seed),self.assertRaises(ValueError):
                self.exam.generate(seed,self.dir/("exam"+str(seed)))

    def test_generated_answer_key_reconciles_events(self):
        output=self.dir/"exam"
        self.exam.generate(500,output)
        rows=[
            json.loads(row)
            for row in (output/"candidate/events.jsonl").read_text().splitlines()
            if row.strip()
        ]
        key=json.loads((output/"reviewer_only/answer_key.json").read_text())
        self.assertEqual(len(rows),5)
        self.assertEqual(key["unique_valid_events"],3)
        self.assertEqual(key["invalid_rows"],1)
        self.assertEqual(len([r for r in rows if r["region_code"]=="bad-region"]),1)


if __name__=="__main__":
    unittest.main()

