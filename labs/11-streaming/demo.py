"""Run Stage 11 offline from a synthetic event log; no Kafka broker needed."""
import json
from pathlib import Path
import sqlite3
from instructor.reference import AckLost, consume, read_log, snapshot

LOG=Path(__file__).resolve().parent/"data/synthetic_log.jsonl"


def main():
    log=read_log(LOG)
    with sqlite3.connect(":memory:") as db:
        try:
            consume(db,log,lose_ack=True)
        except AckLost:
            pass  # this is an expected post-commit acknowledgement failure
        repeated=consume(db,log)
        state=snapshot(db)
        if repeated["status"]!="skipped" or len(state["events"])!=4:
            raise RuntimeError("replay unexpectedly changed the sink")
        print(json.dumps({
            "status":"PASS","mode":"offline simulated Kafka semantics",
            "replay":repeated["status"],**state,
        },indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()

