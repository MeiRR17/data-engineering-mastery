"""Stage 13 capstone reference: end-to-end synthetic DataPulse learning delivery.

Integrates Stage 11 stream checkpoint -> Stage 07 data quality -> Stage 08 read-
only serving -> safe new-file SQLite backup verification -> Stage 09 versioned
artifact staging, promotion and rollback. Zero external network or cloud writes.
"""
from __future__ import annotations

from contextlib import closing
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3

REPO=Path(__file__).resolve().parents[2]
CLOCK=datetime(2026,1,1,12,0,tzinfo=timezone.utc)


def load(path, name):
    spec=spec_from_file_location(name,REPO/path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _readonly_rows(db_path,query):
    conn=sqlite3.connect(Path(db_path).resolve().as_uri()+"?mode=ro",uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        return conn.execute(query).fetchall()
    finally:
        conn.close()


def _full_backup(source,backup,restored):
    """SQLite backup with byte-integrity check, never overwrites existing files."""
    if any(p.exists() or p.is_symlink() for p in (backup,restored)):
        raise FileExistsError("backup and restore destinations must be unused")
    source_db=sqlite3.connect(Path(source).resolve().as_uri()+"?mode=ro",uri=True)
    target=sqlite3.connect(backup)
    try:
        source_db.backup(target)
        target.commit()
    finally:
        target.close()
        source_db.close()
    digest=sha256(backup.read_bytes()).hexdigest()
    restored.write_bytes(backup.read_bytes())  # guarded by prior existence check
    if sha256(restored.read_bytes()).hexdigest()!=digest:
        raise RuntimeError("restored backup SHA mismatch")
    expected=_readonly_rows(source,"select event_id,magnitude from curated_events order by event_id")
    actual=_readonly_rows(restored,"select event_id,magnitude from curated_events order by event_id")
    if expected!=actual or len(actual)!=4:
        raise RuntimeError("restored curated rows differ from source")
    db=sqlite3.connect(restored.resolve().as_uri()+"?mode=ro",uri=True)
    try:
        integrity=db.execute("pragma integrity_check").fetchone()[0]
    finally:
        db.close()
    if integrity!="ok":
        raise RuntimeError("restored SQLite integrity check failed")
    return {"status":"verified","sha256":digest,"rows":len(actual),"integrity":"ok"}


def _release(stage09,root,rows):
    release_dir=root/"build-source"
    release_dir.mkdir()
    (release_dir/"README.txt").write_text(
        "DataPulse synthetic capstone release. Do not deploy this archive.\n"
    )
    def build(version,rows):
        (release_dir/"app.json").write_text(json.dumps({
            "service":"datapulse-training","version":version,"health":"ready",
            "quality":"passed","demo_only":True,"rows":rows
        }))
        return stage09.build_release(release_dir,root/("bundle-"+version),version)
    v1=build("v0.1.0",rows)
    v2=build("v0.2.0",rows)
    verified=stage09.verify_release(*v1)
    deployment=root/"simulated-deployments"
    stage09.deploy_release(*v1,deployment,"dev")
    stage09.deploy_release(*v1,deployment,"staging")
    stage09.deploy_release(*v2,deployment,"staging")
    before=stage09.deployment_status(deployment,"staging")
    if before["version"]!="v0.2.0":
        raise RuntimeError("staging promotion failed")
    stage09.rollback_release(deployment,"staging")
    after=stage09.deployment_status(deployment,"staging")
    dev=stage09.deployment_status(deployment,"dev")
    if after["version"]!="v0.1.0" or dev["version"]!="v0.1.0":
        raise RuntimeError("isolation or rollback failed")
    return {
        "artifact_sha256":verified["metadata"]["sha256"],
        "staging_pre_rollback":before["version"],
        "staging_after_rollback":after["version"],
        "dev_after_staging":dev["version"],
        "simulated_only":True,
    }


def run_pipeline(workspace,*,inject_bad_batch=True,crash_before_stream_commit=False):
    """Create an isolated end-to-end pipeline and evidence in a new directory."""
    root=Path(workspace)
    if root.exists() or root.is_symlink():
        raise FileExistsError("workspace must be a new path, never an existing folder")
    root.mkdir(parents=True)
    stage11=load(Path("labs/11-streaming/instructor/reference.py"),"cap_stream")
    stage07=load(Path("labs/07-quality/instructor/reference.py"),"cap_quality")
    stage08=load(Path("labs/08-serving/service.py"),"cap_serving")
    stage09=load(Path("labs/09-cicd/instructor/reference.py"),"cap_release")

    streaming=root/"stream.sqlite"
    curated=root/"curated.sqlite"
    records=stage11.read_log(REPO/"labs/11-streaming/data/synthetic_log.jsonl")
    with closing(sqlite3.connect(streaming)) as db, db:
        db.execute("pragma foreign_keys=on")
        stage11.consume(db,records,
                        crash_before_commit=crash_before_stream_commit)
        if crash_before_stream_commit:
            raise AssertionError("unreachable crash injection")
        replay=stage11.consume(db,records)
        if replay["status"]!="skipped":
            raise RuntimeError("replay was not idempotent")
        sink_rows=db.execute("""
            select event_id,observed_at,updated_at,region_code,magnitude
            from events order by event_id
        """).fetchall()
        offsets=stage11.snapshot(db)["offsets"]
        dead_letters=stage11.snapshot(db)["dead_letters"]
    if len(sink_rows)!=4:
        raise RuntimeError("stream did not yield 4 curated events")

    upstream=[
        {"event_id":row[0],"observed_at":row[1],
         "source_updated_at":row[2],"region_code":row[3],"magnitude":row[4]}
        for row in sink_rows
    ]
    with closing(sqlite3.connect(curated)) as db, db:
        db.execute("pragma foreign_keys=on")
        contract=stage07.load_contract()
        good=stage07.process_batch(db,"accepted",upstream,CLOCK,contract)
        if not good["passed"] or good["published_rows"]!=4:
            raise RuntimeError("initial quality gate failed")
        bad=None
        if inject_bad_batch:
            drift=deepcopy(upstream)
            drift[0]["unexpected_schema_field"]="synthetic-changed"
            bad=stage07.process_batch(db,"blocked-drift",drift,CLOCK,contract)
            if bad["passed"] or bad["published_rows"]!=0:
                raise RuntimeError("schema drift was not quarantined")
        service=stage08.AnalyticsService(curated,clock=lambda:CLOCK)
        previous=service.overview()
        if inject_bad_batch and previous["last_quality_status"]!="blocked":
            raise RuntimeError("serving failed to expose quality-block state")
        recovered=stage07.process_batch(db,"accepted-replay",upstream,CLOCK,contract)
        if not recovered["passed"] or recovered["published_rows"]!=0:
            raise RuntimeError("recovery replay was not idempotent")
        # Commit, then explicitly close the writer before backup and file cleanup.
        # sqlite3.Connection.__exit__ alone does NOT close the connection on Windows.
    overview=stage08.AnalyticsService(curated,clock=lambda:CLOCK).overview()
    if (overview["total_events"]!=4 or overview["known_magnitude_events"]!=3 or
        overview["average_magnitude"]!=2.7 or overview["last_quality_status"]!="passed"):
        raise RuntimeError("data-serving measures did not reconcile")
    backup=_full_backup(curated,root/"backup.sqlite",root/"restored.sqlite")
    release=_release(stage09,root,overview["total_events"])
    evidence={
        "mode":"offline-synthetic-only",
        "overall_status":"PASS",
        "stream":{"events":len(sink_rows),"dead_letters":len(dead_letters),
                  "offsets":offsets,"replay":"skipped"},
        "data_quality":{
            "accepted":good["published_rows"],
            "drift_blocked":None if bad is None else not bad["passed"],
            "blocked_published":None if bad is None else bad["published_rows"],
            "replay_published":recovered["published_rows"],
        },
        "analytics":{
            "total_events":overview["total_events"],
            "known_magnitude_events":overview["known_magnitude_events"],
            "average_magnitude":overview["average_magnitude"],
            "freshness":overview["freshness_status"],
            "last_quality":overview["last_quality_status"],
        },
        "recovery":backup,
        "release":release,
        "claims":{
            "deployed_to_cloud":False,
            "externally_certified":False,
            "learner_independence_verified":False,
        },
    }
    (root/"evidence.json").write_text(
        json.dumps(evidence,sort_keys=True,indent=2)+"\n",encoding="utf8"
    )
    return evidence

