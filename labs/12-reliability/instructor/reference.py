"""Stage 12 local reliability and recovery oracle, no external systems.

Uses an isolated synthetic SQLite database. Backup restore never overwrites a
destination, and checksum alone is NOT a trusted authentication mechanism.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import sqlite3
from tempfile import NamedTemporaryFile

ROLES={
    "viewer":frozenset(("read_metrics",)),
    "operator":frozenset(("read_metrics","run_backfill","restore_to_new")),
    "admin":frozenset(("read_metrics","run_backfill","restore_to_new","edit_policy")),
}
RUN_STATUS={"success","failed","blocked"}


def authorize(role,action):
    """Least privilege for educational *application actions* (not cloud IAM)."""
    if not isinstance(role,str) or role not in ROLES:
        raise PermissionError("unknown role")
    if not isinstance(action,str) or action not in {
        "read_metrics","run_backfill","restore_to_new","edit_policy"
    }:
        raise PermissionError("unrecognized action")
    if action not in ROLES[role]:
        raise PermissionError("access denied")
    return True


def _instant(value):
    if not isinstance(value,str):
        raise ValueError("timestamp must be ISO string with time zone")
    try:
        dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("naive timestamp")
    return dt.astimezone(timezone.utc)


def compute_slo(runs,events,now,policy):
    """Evaluate window success, freshness and quality against stated thresholds."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone aware")
    if not isinstance(runs,list) or not isinstance(events,list) or not isinstance(policy,dict):
        raise ValueError("runs/events/policy must have expected container types")
    if set(policy)!={"target_availability","max_freshness_hours","max_blocked_fraction"}:
        raise ValueError("unknown SLO policy")
    t,f,q=(policy[k] for k in ("target_availability","max_freshness_hours","max_blocked_fraction"))
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in (t,f,q)):
        raise ValueError("invalid SLO thresholds")
    if not 0<t<=1 or not 0<f<=168 or not 0<=q<=1:
        raise ValueError("SLO thresholds outside safe bounds")
    seen=set()
    for item in runs:
        if (not isinstance(item,dict) or set(item)!={"window","status"} or
            not isinstance(item["window"],str) or not item["window"] or
            item["status"] not in RUN_STATUS or item["window"] in seen):
            raise ValueError("invalid or duplicated run window")
        seen.add(item["window"])
    for event in events:
        if not isinstance(event,dict) or set(event)!={"observed_at"}:
            raise ValueError("invalid event indicator")
    total=len(runs)
    good=sum(x["status"]=="success" for x in runs)
    blocked=sum(x["status"]=="blocked" for x in runs)
    availability=good/total if total else None
    blocked_ratio=blocked/total if total else None
    newest=max((_instant(e["observed_at"]) for e in events),default=None)
    age=(now.astimezone(timezone.utc)-newest).total_seconds()/3600 if newest else None
    freshness=("empty" if age is None else
               "future" if age < -5/60 else
               "stale" if age>f else "fresh")
    allowed=max(0,math.floor(total*(1-t)+1e-12))
    used=total-good
    issues=[]
    if total==0:
        issues.append("NO_RUN_EVIDENCE")
    else:
        if availability<t:
            issues.append("AVAILABILITY_SLO_BREACH")
        if blocked_ratio>q:
            issues.append("QUALITY_BLOCK_RATE")
    if freshness!="fresh":
        issues.append("FRESHNESS_"+freshness.upper())
    return {
        "evaluated_windows":total,"success_windows":good,
        "availability":None if availability is None else round(availability,6),
        "blocked_fraction":None if blocked_ratio is None else round(blocked_ratio,6),
        "allowed_failed_windows":allowed,"used_failed_windows":used,
        "error_budget_remaining":max(0,allowed-used),
        "freshness":freshness,"age_hours":None if age is None else round(age,3),
        "passing":not issues,"issues":issues,
    }


def forecast_cost(events_per_day,bytes_per_event,retention_days,
                  price_per_gib_month,compute_hours,compute_rate):
    """Transparent scenario estimate, not a quote from a cloud provider."""
    inputs=(events_per_day,bytes_per_event,retention_days,
            price_per_gib_month,compute_hours,compute_rate)
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in inputs):
        raise ValueError("cost inputs must be finite, nonnegative numbers")
    if (events_per_day>10**10 or bytes_per_event>10**6 or retention_days>3650
        or price_per_gib_month>1000 or compute_hours>100_000 or compute_rate>10_000):
        raise ValueError("cost estimate bounds exceeded")
    stored_gib=events_per_day*bytes_per_event*retention_days/(1024**3)
    ingestion_gib=events_per_day*bytes_per_event*30/(1024**3)
    storage=stored_gib*price_per_gib_month
    compute=compute_hours*compute_rate
    return {
        "steady_storage_gib":round(stored_gib,4),
        "monthly_ingested_gib":round(ingestion_gib,4),
        "storage_monthly":round(storage,2),
        "compute_monthly":round(compute,2),
        "total_monthly":round(storage+compute,2),
        "caveat":"Excludes requests, network egress, Kafka retention replication, backups and tax",
    }


def create_synthetic_database(path):
    """Create fixture only if the path doesn't exist; never overwrite user files."""
    path=Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError("refusing to overwrite existing database")
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    try:
        db.execute("create table curated(event_id text primary key, magnitude real)")
        db.executemany("insert into curated values (?,?)",[
            ("synthetic-A",1.2),("synthetic-B",4.4),("synthetic-C",None)
        ])
        db.commit()
    finally:
        db.close()
    return path


def _verify_db(path):
    uri=Path(path).resolve().as_uri()+"?mode=ro"
    db=sqlite3.connect(uri,uri=True,timeout=2)
    try:
        result=db.execute("pragma integrity_check").fetchone()
        if not result or result[0]!="ok":
            raise ValueError("SQLite integrity check failed")
        columns=[r[1] for r in db.execute("pragma table_info(curated)")]
        if columns!=["event_id","magnitude"]:
            raise ValueError("unexpected backup schema")
        rows=db.execute("select event_id,magnitude from curated order by event_id").fetchall()
        return rows
    finally:
        db.close()


def backup_database(source,directory,label):
    """SQLite online-backup API; manifest with SHA256; no overwrites or secrets."""
    source,directory=Path(source),Path(directory)
    if (not source.is_file() or source.is_symlink() or
        not isinstance(label,str) or not label.isascii() or
        not label or len(label)>40 or
        not all(ch.isalnum() or ch in "_-" for ch in label)):
        raise ValueError("invalid source or backup label")
    directory.mkdir(parents=True,exist_ok=True)
    archive=directory/(label+".sqlite")
    manifest=directory/(label+".manifest.json")
    if archive.exists() or manifest.exists() or archive.is_symlink() or manifest.is_symlink():
        raise FileExistsError("backup label already used")
    with NamedTemporaryFile(dir=directory,prefix=".stage12-",delete=False) as f:
        temporary=Path(f.name)
    try:
        origin=sqlite3.connect(source.resolve().as_uri()+"?mode=ro",uri=True)
        target=sqlite3.connect(temporary)
        try:
            origin.backup(target)
        finally:
            origin.close()
            target.close()
        records=_verify_db(temporary)
        payload=temporary.read_bytes()
        evidence={"format":"sqlite-v1","name":label+".sqlite",
                  "sha256":sha256(payload).hexdigest(),
                  "size":len(payload),"rows":len(records)}
        # Atomic store for backup bytes. Existing destinations were rejected.
        os.replace(temporary,archive)
        try:
            with manifest.open("x",encoding="utf8") as out:
                json.dump(evidence,out,sort_keys=True)
        except Exception:
            archive.unlink(missing_ok=True)
            raise
    finally:
        temporary.unlink(missing_ok=True)
    return archive,manifest


def verify_backup(archive,manifest):
    archive,manifest=Path(archive),Path(manifest)
    if archive.is_symlink() or manifest.is_symlink():
        raise ValueError("linked backup paths forbidden")
    try:
        entry=json.loads(manifest.read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise ValueError("invalid backup manifest") from exc
    if (not isinstance(entry,dict) or set(entry)!=
        {"format","name","sha256","size","rows"} or
        entry["format"]!="sqlite-v1" or entry["name"]!=archive.name or
        not isinstance(entry["sha256"],str) or len(entry["sha256"])!=64 or
        any(c not in "0123456789abcdef" for c in entry["sha256"]) or
        type(entry["size"]) is not int or entry["size"]<100 or
        type(entry["rows"]) is not int or entry["rows"]<0):
        raise ValueError("unsupported backup manifest")
    try:
        content=archive.read_bytes()
    except OSError as exc:
        raise ValueError("backup bytes unavailable") from exc
    if len(content)!=entry["size"] or sha256(content).hexdigest()!=entry["sha256"]:
        raise ValueError("backup checksum mismatch")
    if len(_verify_db(archive))!=entry["rows"]:
        raise ValueError("backup record count mismatch")
    return entry


def restore_to_new(archive,manifest,destination):
    """Verify and restore into a *new* path; never overwrite a live database."""
    archive,manifest,destination=Path(archive),Path(manifest),Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("refuse to overwrite existing destination")
    entry=verify_backup(archive,manifest)
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation guards against accidental overwrite.
    try:
        with destination.open("xb") as out:
            out.write(archive.read_bytes())
            out.flush()
            os.fsync(out.fileno())
        if len(_verify_db(destination))!=entry["rows"]:
            raise ValueError("restored record count mismatch")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return {"restored_rows":entry["rows"],"sha256":entry["sha256"],
            "status":"restored-to-new-path"}

