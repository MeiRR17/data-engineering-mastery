"""Stage 12 independent grading suite; --reference checks instructor baseline."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

LAB=Path(__file__).resolve().parent
TARGET=None
NOW=datetime(2026,1,3,12,0,tzinfo=timezone.utc)
POLICY={"target_availability":0.9,"max_freshness_hours":24,
        "max_blocked_fraction":0.1}
RUNS=[{"window":f"window-{i}","status":"success"} for i in range(10)]
EVENTS=[{"observed_at":"2026-01-03T11:00:00Z"}]


class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(prefix="dem-stage12-")
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)

    def synthetic(self):
        from importlib.util import module_from_spec, spec_from_file_location
        p=LAB/"instructor/reference.py"
        spec=spec_from_file_location("stage12_fixture",p)
        fixture=module_from_spec(spec)
        spec.loader.exec_module(fixture)
        return fixture.create_synthetic_database(self.base/"source.sqlite")

    def backup(self):
        return TARGET.backup_database(self.synthetic(),self.base/"backups","snapshot-01")

    def test_viewer_can_read_but_not_modify(self):
        self.assertTrue(TARGET.authorize("viewer","read_metrics"))
        with self.assertRaises(PermissionError):
            TARGET.authorize("viewer","restore_to_new")

    def test_operator_can_restore_but_not_edit_policy(self):
        self.assertTrue(TARGET.authorize("operator","restore_to_new"))
        with self.assertRaises(PermissionError):
            TARGET.authorize("operator","edit_policy")

    def test_admin_can_edit_policy(self):
        self.assertTrue(TARGET.authorize("admin","edit_policy"))

    def test_unknown_roles_and_actions_rejected(self):
        for role,action in [("root","read_metrics"),("viewer","drop_table"),
                            ("", "read_metrics"),("admin","expose_secrets")]:
            with self.subTest(role=role,action=action),self.assertRaises(PermissionError):
                TARGET.authorize(role,action)

    def test_green_slo(self):
        report=TARGET.compute_slo(RUNS,EVENTS,NOW,POLICY)
        self.assertTrue(report["passing"])
        self.assertEqual(report["availability"],1.0)
        self.assertEqual(report["freshness"],"fresh")
        self.assertEqual(report["allowed_failed_windows"],1)
        self.assertEqual(report["error_budget_remaining"],1)

    def test_one_failed_window_consumes_error_budget(self):
        runs=[dict(x) for x in RUNS]
        runs[4]["status"]="failed"
        report=TARGET.compute_slo(runs,EVENTS,NOW,POLICY)
        self.assertEqual(report["availability"],0.9)
        self.assertEqual(report["used_failed_windows"],1)
        self.assertEqual(report["error_budget_remaining"],0)
        self.assertTrue(report["passing"])

    def test_two_failed_windows_breach(self):
        runs=[dict(x) for x in RUNS]
        for n in (3,4):
            runs[n]["status"]="failed"
        report=TARGET.compute_slo(runs,EVENTS,NOW,POLICY)
        self.assertFalse(report["passing"])
        self.assertIn("AVAILABILITY_SLO_BREACH",report["issues"])

    def test_blocked_fraction_triggers_alert(self):
        runs=[dict(x) for x in RUNS]
        runs[3]["status"]="blocked"
        runs[4]["status"]="blocked"
        report=TARGET.compute_slo(runs,EVENTS,NOW,POLICY)
        self.assertIn("QUALITY_BLOCK_RATE",report["issues"])

    def test_stale_data_alert(self):
        result=TARGET.compute_slo(
            RUNS,[{"observed_at":"2026-01-01T10:00:00Z"}],NOW,POLICY
        )
        self.assertEqual(result["freshness"],"stale")
        self.assertIn("FRESHNESS_STALE",result["issues"])

    def test_empty_events_alert(self):
        result=TARGET.compute_slo(RUNS,[],NOW,POLICY)
        self.assertEqual(result["freshness"],"empty")
        self.assertFalse(result["passing"])

    def test_empty_runs_do_not_count_as_good(self):
        result=TARGET.compute_slo([],EVENTS,NOW,POLICY)
        self.assertIn("NO_RUN_EVIDENCE",result["issues"])
        self.assertIsNone(result["availability"])

    def test_future_clock_skew_alert(self):
        result=TARGET.compute_slo(
            RUNS,[{"observed_at":"2026-01-03T15:00:00Z"}],NOW,POLICY
        )
        self.assertEqual(result["freshness"],"future")

    def test_duplicate_windows_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.compute_slo(RUNS+[RUNS[0]],EVENTS,NOW,POLICY)

    def test_naive_clock_and_bad_policy_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.compute_slo(RUNS,EVENTS,datetime(2026,1,1),POLICY)
        with self.assertRaises(ValueError):
            TARGET.compute_slo(RUNS,EVENTS,NOW,
               {**POLICY,"target_availability":1.5})

    def test_cost_zero_scenario(self):
        report=TARGET.forecast_cost(0,500,30,0.02,0,0.1)
        self.assertEqual(report["total_monthly"],0)
        self.assertEqual(report["steady_storage_gib"],0)

    def test_cost_formula_units(self):
        report=TARGET.forecast_cost(1024,1024,1,1.0,10,2.0)
        self.assertEqual(report["steady_storage_gib"],0.001)
        self.assertEqual(report["compute_monthly"],20)
        self.assertEqual(report["total_monthly"],20.0)

    def test_cost_negative_invalid_or_unbounded_rejected(self):
        for values in [(-1,10,30,1,10,1),(1,float("nan"),30,1,10,1),
                       (1,10,4000,1,10,1),(1,10,30,1,True,1)]:
            with self.subTest(values=values),self.assertRaises(ValueError):
                TARGET.forecast_cost(*values)

    def test_backup_integrity_and_row_count(self):
        archive,manifest=self.backup()
        report=TARGET.verify_backup(archive,manifest)
        self.assertEqual(report["rows"],3)
        self.assertEqual(report["name"],archive.name)

    def test_restored_file_matches_source_data(self):
        archive,manifest=self.backup()
        restore=self.base/"restored.sqlite"
        result=TARGET.restore_to_new(archive,manifest,restore)
        self.assertEqual(result["restored_rows"],3)
        with closing(sqlite3.connect(restore)) as db, db:
            self.assertEqual(db.execute("select count(*) from curated").fetchone()[0],3)

    def test_restore_cannot_overwrite_live_file(self):
        source=self.synthetic()
        archive,manifest=TARGET.backup_database(source,self.base/"b","s1")
        with self.assertRaises(FileExistsError):
            TARGET.restore_to_new(archive,manifest,source)

    def test_corrupt_archive_refused(self):
        archive,manifest=self.backup()
        archive.write_bytes(archive.read_bytes()+b"tampering")
        with self.assertRaises(ValueError):
            TARGET.verify_backup(archive,manifest)

    def test_corrupt_manifest_refused(self):
        archive,manifest=self.backup()
        data=json.loads(manifest.read_text())
        data["sha256"]="0"*64
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            TARGET.restore_to_new(archive,manifest,self.base/"restored.sqlite")
        self.assertFalse((self.base/"restored.sqlite").exists())

    def test_same_backup_label_must_not_overwrite(self):
        source=self.synthetic()
        TARGET.backup_database(source,self.base/"b","snapshot")
        with self.assertRaises(FileExistsError):
            TARGET.backup_database(source,self.base/"b","snapshot")

    def test_backup_label_traversal_rejected(self):
        source=self.synthetic()
        with self.assertRaises(ValueError):
            TARGET.backup_database(source,self.base/"b","../../bad")

    def test_symlinked_backup_source_rejected(self):
        original=self.synthetic()
        shortcut=self.base/"shortcut.sqlite"
        shortcut.symlink_to(original)
        with self.assertRaises(ValueError):
            TARGET.backup_database(shortcut,self.base/"b","linked")

    def test_rollback_plan_never_overwrites_live_state(self):
        archive,manifest=self.backup()
        destination=self.base/"production.sqlite"
        destination.write_text("existing live data must be preserved")
        with self.assertRaises(FileExistsError):
            TARGET.restore_to_new(archive,manifest,destination)
        self.assertIn("preserved",destination.read_text())

    def test_backup_works_from_open_wal_connection(self):
        source=self.synthetic()
        writer=sqlite3.connect(source)
        writer.execute("pragma journal_mode=wal")
        writer.execute("insert into curated values ('synthetic-D',3.5)")
        writer.commit()
        archive,manifest=TARGET.backup_database(source,self.base/"b","wal")
        writer.close()
        self.assertEqual(TARGET.verify_backup(archive,manifest)["rows"],4)


def main():
    global TARGET
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference",action="store_true")
    args=parser.parse_args()
    path=LAB/("instructor/reference.py" if args.reference else "starter.py")
    spec=spec_from_file_location("stage12_target",path)
    TARGET=module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ReliabilityTests))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":
    raise SystemExit(main())

