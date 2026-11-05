"""Stage 11 streaming semantics grader; default checks unfinished student code."""
import argparse
import copy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3
import unittest

LAB=Path(__file__).resolve().parent
TARGET=None


def sample():
    return [json.loads(x) for x in (LAB/"data/synthetic_log.jsonl").read_text().splitlines() if x.strip()]


def event(event_id="A",time="2026-01-01T10:00:00Z",
          updated="2026-01-01T10:05:00Z",magnitude=2.5):
    return {"event_id":event_id,"observed_at":time,
            "source_updated_at":updated,"region_code":"N","magnitude":magnitude}


def msg(partition,offset,value):
    return {"partition":partition,"offset":offset,"value":value}


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.db.execute("pragma foreign_keys=on")

    def tearDown(self):
        self.db.close()

    def consume(self,messages,**kwargs):
        return TARGET.consume(self.db,messages,**kwargs)

    def test_synthetic_log_has_expected_semantics(self):
        output=self.consume(sample())
        self.assertEqual((output["processed"],output["accepted"],output["rejected"],
                          output["late"],output["duplicates"]),(8,5,2,1,1))
        state=TARGET.snapshot(self.db)
        self.assertEqual([x["event_id"] for x in state["events"]],
                         ["evt-A","evt-B","evt-C","evt-E"])
        self.assertEqual(state["offsets"],[
            {"partition":0,"next_offset":4},{"partition":1,"next_offset":4}
        ])

    def test_newer_update_wins_across_partitions(self):
        self.consume(sample())
        self.assertEqual(self.db.execute(
            "select magnitude from events where event_id='evt-A'").fetchone()[0],1.8)

    def test_stale_update_never_overwrites(self):
        self.consume(sample())
        self.assertEqual(self.db.execute(
            "select magnitude from events where event_id='evt-B'").fetchone()[0],4.1)

    def test_watermark_rejects_late_event(self):
        self.consume(sample())
        self.assertEqual(self.db.execute(
            "select reason_code from dead_letters where partition_id=0 and offset_id=3"
        ).fetchone()[0],"LATE_EVENT")

    def test_poison_message_does_not_block_offsets(self):
        self.consume(sample())
        self.assertEqual(self.db.execute(
            "select reason_code from dead_letters where partition_id=1 and offset_id=2"
        ).fetchone()[0],"NAIVE_TIMESTAMP")
        self.assertEqual(self.db.execute("select next_offset from consumer_offsets "
                          "where partition_id=1").fetchone()[0],4)

    def test_replay_is_skipped(self):
        self.consume(sample())
        self.assertEqual(self.consume(sample())["status"],"skipped")
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],4)

    def test_crash_before_commit_rolls_back_sink_and_offsets(self):
        with self.assertRaises(RuntimeError):
            self.consume(sample(),crash_before_commit=True)
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],0)
        self.assertEqual(self.db.execute("select count(*) from consumer_offsets").fetchone()[0],0)
        self.assertEqual(self.db.execute("select count(*) from dead_letters").fetchone()[0],0)
        self.assertEqual(self.consume(sample())["status"],"committed")

    def test_lost_ack_after_commit_restarts_without_duplicates(self):
        with self.assertRaises(TARGET.AckLost):
            self.consume(sample(),lose_ack=True)
        self.assertEqual(self.consume(sample())["status"],"skipped")
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],4)

    def test_bounded_batch_advances_offsets_only_for_processed_records(self):
        first=self.consume(sample(),max_records=2)
        self.assertEqual(first["processed"],2)
        self.assertEqual(self.db.execute("select next_offset from consumer_offsets "
                          "where partition_id=0").fetchone()[0],2)
        self.assertEqual(self.consume(sample(),max_records=2)["processed"],2)
        self.assertEqual(self.db.execute("select next_offset from consumer_offsets "
                          "where partition_id=0").fetchone()[0],4)
        self.assertEqual(self.consume(sample(),max_records=2)["processed"],2)

    def test_empty_batch_is_safe(self):
        self.assertEqual(self.consume([])["status"],"skipped")

    def test_log_order_independent_within_partition(self):
        baseline=self.consume(sample())
        before=TARGET.snapshot(self.db)
        second=sqlite3.connect(":memory:")
        try:
            TARGET.consume(second,list(reversed(sample())))
            self.assertEqual(TARGET.snapshot(second),before)
        finally:
            second.close()

    def test_same_partition_offset_conflict_rejected(self):
        m=msg(0,0,event())
        changed=copy.deepcopy(m)
        changed["value"]["magnitude"]=9.0
        with self.assertRaises(ValueError):
            self.consume([m,changed])

    def test_repeated_envelope_rejected(self):
        m=msg(0,0,event())
        with self.assertRaises(ValueError):
            self.consume([m,m])

    def test_negative_partition_or_offset_rejected(self):
        for p,o in [(-1,0),(32,0),(0,-1),(True,0),(0,False)]:
            with self.subTest(p=p,o=o),self.assertRaises(ValueError):
                self.consume([msg(p,o,event())])

    def test_group_and_topic_scope_validated(self):
        with self.assertRaises(ValueError):
            self.consume([msg(0,0,event())],group_id="../../other")
        with self.assertRaises(ValueError):
            self.consume([msg(0,0,event())],topic="production")

    def test_max_records_is_bounded(self):
        for limit in (0,10001,True,"10"):
            with self.subTest(limit=limit),self.assertRaises(ValueError):
                self.consume(sample(),max_records=limit)

    def test_lateness_window_is_bounded(self):
        for limit in (-1,1441,True,1.5):
            with self.subTest(limit=limit),self.assertRaises(ValueError):
                self.consume(sample(),allowed_lateness_minutes=limit)

    def test_null_is_retained_as_null(self):
        self.consume([msg(0,0,event(magnitude=None))])
        self.assertIsNone(self.db.execute("select magnitude from events").fetchone()[0])

    def test_bad_json_schema_quarantine_is_safe(self):
        report=self.consume([msg(0,0,{"private_token":"do-not-leak"})])
        self.assertEqual(report["rejected"],1)
        state=json.dumps(TARGET.snapshot(self.db))
        self.assertNotIn("do-not-leak",state)
        self.assertIn("SCHEMA_MISMATCH",state)

    def test_tie_timestamp_content_stable_for_any_order(self):
        a=msg(0,0,event(magnitude=3))
        b=msg(1,0,event(magnitude=8))
        self.consume([a,b])
        one=TARGET.snapshot(self.db)["events"]
        other=sqlite3.connect(":memory:")
        try:
            TARGET.consume(other,[b,a])
            self.assertEqual(TARGET.snapshot(other)["events"],one)
        finally:
            other.close()

    def test_offset_gap_allowed_like_compacted_log(self):
        out=self.consume([msg(0,5,event("A"))])
        self.assertEqual(out["processed"],1)
        self.assertEqual(TARGET.snapshot(self.db)["offsets"][0]["next_offset"],6)

    def test_second_consumer_group_independent_checkpoint(self):
        self.consume([msg(0,0,event())],group_id="alpha")
        self.assertEqual(self.consume([msg(0,0,event())],group_id="beta")["processed"],1)
        self.assertEqual(self.db.execute("select count(*) from consumer_offsets").fetchone()[0],2)
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],1)

    def test_update_before_event_rejected(self):
        self.consume([msg(0,0,event(updated="2025-12-31T23:00:00Z"))])
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],0)
        self.assertIn("UPDATE_BEFORE_EVENT",json.dumps(TARGET.snapshot(self.db)))

    def test_timestamp_offset_normalized_to_utc(self):
        self.consume([msg(0,0,event(time="2026-01-02T00:30:00+02:00",
                                   updated="2026-01-02T00:35:00+02:00"))])
        self.assertTrue(self.db.execute("select observed_at from events").fetchone()[0]
                        .startswith("2026-01-01T22:30"))

    def test_rebalance_restart_from_checkpoint(self):
        records=[msg(0,0,event("A")),msg(0,1,event("B")),msg(0,2,event("C"))]
        self.consume(records,max_records=1)
        second=self.consume(records,max_records=1)
        third=self.consume(records,max_records=1)
        self.assertEqual([second["processed"],third["processed"]],[1,1])
        self.assertEqual(TARGET.snapshot(self.db)["offsets"],[{"partition":0,"next_offset":3}])
        self.assertEqual(self.db.execute("select count(*) from events").fetchone()[0],3)


def main():
    global TARGET
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference",action="store_true")
    args=parser.parse_args()
    filename=LAB/("instructor/reference.py" if args.reference else "starter.py")
    spec=spec_from_file_location("stream_target",filename)
    TARGET=module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(StreamTests))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":
    raise SystemExit(main())

