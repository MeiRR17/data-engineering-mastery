"""Offline Kafka-semantics lab: durable partition offsets, idempotent sink and replay.

This teaches broker-delivery failure semantics with a local SQLite transaction.
It does NOT claim Kafka's cross-system exactly-once guarantee. No network or
third-party runtime required; the optional broker adapter is separate.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

TOPIC = "synthetic-events"
REQUIRED = {"event_id","observed_at","source_updated_at","region_code","magnitude"}
ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
REGION = re.compile(r"[A-Z]{1,8}\Z")


class AckLost(RuntimeError):
    """Committed effects and checkpoints, but the response was lost."""


class InvalidEvent(ValueError):
    def __init__(self, code):
        self.code=code
        super().__init__(code)


def ensure_schema(db):
    db.executescript("""
    create table if not exists events(
      event_id text primary key, region_code text not null,
      observed_at text not null, updated_at text not null,
      magnitude real, payload_digest text not null
    );
    create table if not exists consumer_offsets(
      group_id text not null, topic text not null,
      partition_id integer not null, next_offset integer not null
        check(next_offset >= 0),
      primary key(group_id,topic,partition_id)
    );
    create table if not exists dead_letters(
      group_id text not null, topic text not null,
      partition_id integer not null, offset_id integer not null,
      reason_code text not null,
      primary key(group_id,topic,partition_id,offset_id)
    );
    """)


def parse_time(value):
    if not isinstance(value,str):
        raise InvalidEvent("INVALID_TIMESTAMP")
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc:
        raise InvalidEvent("INVALID_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InvalidEvent("NAIVE_TIMESTAMP")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00","Z")


def normalize(value):
    if not isinstance(value,dict) or set(value)!=REQUIRED:
        raise InvalidEvent("SCHEMA_MISMATCH")
    event=value["event_id"]
    region=value["region_code"]
    if not isinstance(event,str) or not ID.fullmatch(event):
        raise InvalidEvent("INVALID_EVENT_ID")
    if not isinstance(region,str) or not REGION.fullmatch(region):
        raise InvalidEvent("INVALID_REGION")
    magnitude=value["magnitude"]
    if magnitude is not None and (
        type(magnitude) not in (int,float) or magnitude != magnitude or
        not -5 <= magnitude <= 12):
        raise InvalidEvent("INVALID_MAGNITUDE")
    seen=parse_time(value["observed_at"])
    changed=parse_time(value["source_updated_at"])
    if changed < seen:
        raise InvalidEvent("UPDATE_BEFORE_EVENT")
    result=dict(
        event_id=event, region_code=region, observed_at=seen,
        updated_at=changed, magnitude=None if magnitude is None else float(magnitude)
    )
    digest=sha256(json.dumps(
        result,sort_keys=True,separators=(",",":"),ensure_ascii=False
    ).encode("utf8")).hexdigest()
    return {**result,"payload_digest":digest}


def read_log(path):
    """Decode bounded synthetic JSONL; preserve partition/offset identity."""
    messages=[]
    for n,line in enumerate(Path(path).read_text(encoding="utf8").splitlines(),1):
        if not line.strip():
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError("invalid log envelope at line "+str(n)) from exc
    return messages


def consume(db, messages, *, group_id="classroom", topic=TOPIC,
            allowed_lateness_minutes=90, max_records=1000,
            crash_before_commit=False, lose_ack=False):
    """Atomically persist sink changes and per-partition *next* offsets.

    This is a deterministic single-batch, single-owner consumer. The watermark
    for the batch is max(valid event time) minus allowed_lateness_minutes.
    It is NOT a stateful distributed streaming watermark across rebalances.
    """
    if db.in_transaction:
        raise ValueError("finish previous transaction")
    if not isinstance(group_id,str) or not ID.fullmatch(group_id):
        raise ValueError("invalid consumer group")
    if topic!=TOPIC:
        raise ValueError("unrecognized topic")
    if type(allowed_lateness_minutes) is not int or not 0<=allowed_lateness_minutes<=1440:
        raise ValueError("lateness must be 0..1440 minutes")
    if type(max_records) is not int or not 1<=max_records<=10000:
        raise ValueError("max_records must be bounded")
    if not isinstance(messages,list):
        raise ValueError("messages must be a list")
    envelopes={}
    for msg in messages:
        if not isinstance(msg,dict) or set(msg)!={"partition","offset","value"}:
            raise ValueError("invalid log envelope")
        p,o=msg["partition"],msg["offset"]
        if type(p) is not int or type(o) is not int or p<0 or p>31 or o<0:
            raise ValueError("invalid partition/offset")
        key=(p,o)
        if key in envelopes:
            if envelopes[key]!=msg:
                raise ValueError("conflicting data at same topic-partition-offset")
            raise ValueError("repeated topic-partition-offset in input")
        envelopes[key]=msg
    ensure_schema(db)
    # Ordered partition sequence, with no unbounded background processing.
    cursor_offsets={
        row[0]:row[1] for row in db.execute(
            "select partition_id,next_offset from consumer_offsets where group_id=? and topic=?",
            (group_id,topic)
        ).fetchall()
    }
    pending=[(p,o,m) for (p,o),m in sorted(envelopes.items())
             if o>=cursor_offsets.get(p,0)][:max_records]
    if not pending:
        return {"status":"skipped","processed":0,"accepted":0,"rejected":0,
                "late":0,"duplicates":0}
    validated=[]
    for p,o,msg in pending:
        try:
            value=normalize(msg["value"])
            validated.append((p,o,value,None))
        except InvalidEvent as error:
            validated.append((p,o,None,error.code))
    event_times=[datetime.fromisoformat(e["observed_at"].replace("Z","+00:00"))
                 for _,_,e,_ in validated if e is not None]
    watermark=(max(event_times)-timedelta(minutes=allowed_lateness_minutes)
               if event_times else None)
    stats={"status":"committed","processed":len(pending),"accepted":0,
           "rejected":0,"late":0,"duplicates":0}
    highest={}
    try:
        db.execute("begin immediate")
        for p,o,value,error in validated:
            highest[p]=max(highest.get(p,-1),o)
            if value is not None and watermark is not None and (
                datetime.fromisoformat(value["observed_at"].replace("Z","+00:00"))<watermark
            ):
                error="LATE_EVENT"
                stats["late"]+=1
            if error:
                db.execute("""
                  insert or ignore into dead_letters
                    (group_id,topic,partition_id,offset_id,reason_code)
                  values(?,?,?,?,?)
                """,(group_id,topic,p,o,error))
                stats["rejected"]+=1
                continue
            result=db.execute("""
              insert into events(event_id,region_code,observed_at,updated_at,
                                 magnitude,payload_digest)
              values(?,?,?,?,?,?)
              on conflict(event_id) do update set
                region_code=excluded.region_code,
                observed_at=excluded.observed_at,
                updated_at=excluded.updated_at,
                magnitude=excluded.magnitude,
                payload_digest=excluded.payload_digest
              where (excluded.updated_at,excluded.payload_digest)>
                    (events.updated_at,events.payload_digest)
            """,(
                value["event_id"],value["region_code"],value["observed_at"],
                value["updated_at"],value["magnitude"],value["payload_digest"]
            ))
            if result.rowcount==1:
                stats["accepted"]+=1
            else:
                stats["duplicates"]+=1
        for p,latest in highest.items():
            db.execute("""
              insert into consumer_offsets(group_id,topic,partition_id,next_offset)
              values(?,?,?,?)
              on conflict(group_id,topic,partition_id) do update set
                next_offset=max(consumer_offsets.next_offset,excluded.next_offset)
            """,(group_id,topic,p,latest+1))
        if crash_before_commit:
            raise RuntimeError("simulated crash before atomic transaction commit")
        db.commit()
    except BaseException:
        db.rollback()
        raise
    if lose_ack:
        raise AckLost("commit succeeded but caller did not receive acknowledgement")
    return stats


def snapshot(db):
    """Stable serving projection; never return private dead-letter payloads."""
    events=[
        {"event_id":r[0],"region_code":r[1],"observed_at":r[2],"magnitude":r[3]}
        for r in db.execute(
            "select event_id,region_code,observed_at,magnitude from events order by event_id"
        )
    ]
    offsets=[
        {"partition":r[0],"next_offset":r[1]}
        for r in db.execute(
            "select partition_id,next_offset from consumer_offsets "
            "where group_id='classroom' and topic=? order by partition_id",(TOPIC,)
        )
    ]
    rejects=[
        {"partition":r[0],"offset":r[1],"reason":r[2]}
        for r in db.execute(
            "select partition_id,offset_id,reason_code from dead_letters "
            "where group_id='classroom' and topic=? "
            "order by partition_id,offset_id",(TOPIC,)
        )
    ]
    return {"events":events,"offsets":offsets,"dead_letters":rejects}

