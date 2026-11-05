"""Stage 13 portfolio capstone grader. --reference validates instructor pipeline.

Default targets starter.py which must be implemented independently.
All tests use temporary directories and synthetic fixture data only.
"""
from __future__ import annotations
import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

CAP=Path(__file__).resolve().parent
ROOT=CAP.parent
TARGET=None


class CapstoneTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(prefix="dem-capstone-grade-")
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)
        self.out=self.dir/"output"

    def run_capstone(self,**kwargs):
        return TARGET.run_pipeline(self.out,**kwargs)

    def test_complete_evidence_schema(self):
        report=self.run_capstone()
        self.assertEqual(set(report),{
            "mode","overall_status","stream","data_quality","analytics",
            "recovery","release","claims"
        })
        self.assertEqual(report["overall_status"],"PASS")

    def test_evidence_file_is_reproducible_json(self):
        report=self.run_capstone()
        saved=json.loads((self.out/"evidence.json").read_text())
        self.assertEqual(saved,report)

    def test_stream_event_grain(self):
        report=self.run_capstone()
        self.assertEqual(report["stream"]["events"],4)
        with sqlite3.connect(self.out/"stream.sqlite") as db:
            self.assertEqual(db.execute("select count(*) from events").fetchone()[0],4)

    def test_stream_checkpoint_offsets(self):
        report=self.run_capstone()
        self.assertEqual(report["stream"]["offsets"],[
            {"partition":0,"next_offset":4},{"partition":1,"next_offset":4}
        ])
        self.assertEqual(report["stream"]["replay"],"skipped")

    def test_deadletter_quarantine_has_no_payload_column(self):
        report=self.run_capstone()
        self.assertEqual(report["stream"]["dead_letters"],2)
        with sqlite3.connect(self.out/"stream.sqlite") as db:
            cols={row[1] for row in db.execute("pragma table_info(dead_letters)")}
        self.assertNotIn("payload",cols)
        self.assertIn("reason_code",cols)

    def test_quality_good_run_publishes_four(self):
        report=self.run_capstone()
        self.assertEqual(report["data_quality"]["accepted"],4)
        with sqlite3.connect(self.out/"curated.sqlite") as db:
            self.assertEqual(db.execute("select count(*) from curated_events").fetchone()[0],4)

    def test_bad_schema_batch_blocked_without_publish(self):
        report=self.run_capstone()
        self.assertTrue(report["data_quality"]["drift_blocked"])
        self.assertEqual(report["data_quality"]["blocked_published"],0)
        with sqlite3.connect(self.out/"curated.sqlite") as db:
            row=db.execute("select status,published_rows from quality_runs "
                           "where run_id='blocked-drift'").fetchone()
        self.assertEqual(row,("blocked",0))

    def test_quality_recovery_replay_is_idempotent(self):
        report=self.run_capstone()
        self.assertEqual(report["data_quality"]["replay_published"],0)
        with sqlite3.connect(self.out/"curated.sqlite") as db:
            self.assertEqual(db.execute(
                "select status from quality_runs where run_id='accepted-replay'").fetchone()[0],
                "passed")

    def test_serving_metrics_are_correct(self):
        report=self.run_capstone()
        self.assertEqual(report["analytics"]["total_events"],4)
        self.assertEqual(report["analytics"]["known_magnitude_events"],3)
        self.assertEqual(report["analytics"]["average_magnitude"],2.7)

    def test_serving_distinguishes_freshness_and_last_quality(self):
        report=self.run_capstone()
        self.assertEqual(report["analytics"]["freshness"],"fresh")
        self.assertEqual(report["analytics"]["last_quality"],"passed")

    def test_backup_and_restored_dataset_match(self):
        report=self.run_capstone()
        self.assertEqual(report["recovery"]["integrity"],"ok")
        self.assertEqual(report["recovery"]["rows"],4)
        with sqlite3.connect(self.out/"restored.sqlite") as db:
            restored=db.execute("select event_id,magnitude from curated_events order by event_id").fetchall()
        with sqlite3.connect(self.out/"curated.sqlite") as db:
            original=db.execute("select event_id,magnitude from curated_events order by event_id").fetchall()
        self.assertEqual(restored,original)

    def test_restore_does_not_modify_source_backup(self):
        self.run_capstone()
        digest=(self.out/"backup.sqlite").read_bytes()
        self.assertEqual(digest,(self.out/"restored.sqlite").read_bytes())

    def test_release_artifact_exists_and_digest_matches(self):
        report=self.run_capstone()
        artifact=self.out/"bundle-v0.1.0"/"datapulse-v0.1.0.zip"
        self.assertTrue(artifact.is_file())
        from hashlib import sha256
        self.assertEqual(sha256(artifact.read_bytes()).hexdigest(),
                         report["release"]["artifact_sha256"])

    def test_release_deployment_and_rollback(self):
        report=self.run_capstone()
        self.assertEqual(report["release"]["staging_pre_rollback"],"v0.2.0")
        self.assertEqual(report["release"]["staging_after_rollback"],"v0.1.0")
        self.assertEqual(report["release"]["dev_after_staging"],"v0.1.0")

    def test_release_is_explicitly_a_simulation(self):
        report=self.run_capstone()
        self.assertTrue(report["release"]["simulated_only"])
        self.assertEqual(report["mode"],"offline-synthetic-only")

    def test_no_forged_external_certification_claims(self):
        report=self.run_capstone()
        claims=report["claims"]
        self.assertIs(claims["deployed_to_cloud"],False)
        self.assertIs(claims["externally_certified"],False)
        self.assertIs(claims["learner_independence_verified"],False)

    def test_bad_batch_optional(self):
        report=self.run_capstone(inject_bad_batch=False)
        self.assertIsNone(report["data_quality"]["drift_blocked"])
        self.assertIsNone(report["data_quality"]["blocked_published"])

    def test_workspace_is_never_overwritten(self):
        self.out.mkdir()
        sentinel=self.out/"existing.txt"
        sentinel.write_text("never change")
        with self.assertRaises(FileExistsError):
            self.run_capstone()
        self.assertEqual(sentinel.read_text(),"never change")

    def test_stream_crash_blocks_downstream_and_rolls_back(self):
        with self.assertRaises(RuntimeError):
            self.run_capstone(crash_before_stream_commit=True)
        self.assertFalse((self.out/"curated.sqlite").exists())
        self.assertFalse((self.out/"evidence.json").exists())
        if (self.out/"stream.sqlite").exists():
            with sqlite3.connect(self.out/"stream.sqlite") as db:
                self.assertEqual(db.execute("select count(*) from events").fetchone()[0],0)
                self.assertEqual(db.execute(
                    "select count(*) from consumer_offsets").fetchone()[0],0)

    def test_no_workspace_paths_or_sensitive_fields_in_evidence(self):
        report=self.run_capstone()
        content=json.dumps(report)
        self.assertNotIn(str(self.dir),content)
        for secret in ("private_token","source_updated_at","raw_payload","localhost:5432"):
            self.assertNotIn(secret,content)

    def test_source_fixture_is_not_modified(self):
        fixture=ROOT/"labs/11-streaming/data/synthetic_log.jsonl"
        before=fixture.read_bytes()
        self.run_capstone()
        self.assertEqual(before,fixture.read_bytes())

    def test_stream_to_curated_id_and_magnitude_reconciliation(self):
        self.run_capstone()
        with sqlite3.connect(self.out/"stream.sqlite") as s,sqlite3.connect(self.out/"curated.sqlite") as c:
            stream=s.execute("select event_id,magnitude from events order by event_id").fetchall()
            curated=c.execute(
                "select event_id,magnitude from curated_events order by event_id").fetchall()
        self.assertEqual(stream,curated)


def main():
    global TARGET
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference",action="store_true")
    args=parser.parse_args()
    path=CAP/("instructor/reference.py" if args.reference else "starter.py")
    spec=spec_from_file_location("capstone_target",path)
    TARGET=module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    results=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CapstoneTests))
    return 0 if results.wasSuccessful() else 1


if __name__=="__main__":
    raise SystemExit(main())

