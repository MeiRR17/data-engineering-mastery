"""Reference implementation of a fail-closed, auditable learning pipeline.

All inputs are synthetic. No cloud calls, environment access or network access.
For each batch, structural errors are quarantined without storing raw payloads.
A quality gate decides whether any validated records may become curated data.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from heapq import heappop, heappush
import json
import math
import re
import sqlite3
from pathlib import Path


LAB = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"


class RowProblem(ValueError):
    """A controlled, non-sensitive reason code for rejecting a row."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def load_contract(path: Path | None = None) -> dict:
    """Read the local teaching contract; enforce supported schema version."""
    cfg = json.loads(Path(path or LAB / "contract.json").read_text(encoding="utf8"))
    expected = ["event_id", "observed_at", "source_updated_at", "region_code", "magnitude"]
    if (cfg.get("schema_version") != VERSION or
        cfg.get("required_fields") != expected or
        cfg.get("name") != "synthetic-earthquake-events"):
        raise ValueError("unsupported data contract")
    for key in ("min_valid_ratio", "min_magnitude_completeness", "max_stale_ratio"):
        n = cfg.get(key)
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not 0 <= n <= 1:
            raise ValueError("invalid quality threshold")
    for key in ("max_future_skew_minutes", "max_freshness_hours"):
        n = cfg.get(key)
        if isinstance(n, bool) or not isinstance(n, (int, float)) or n <= 0:
            raise ValueError("invalid time threshold")
    return cfg


def _parse_time(value) -> datetime:
    if not isinstance(value, str):
        raise RowProblem("BAD_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RowProblem("BAD_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RowProblem("NAIVE_TIMESTAMP")
    return parsed.astimezone(timezone.utc)


def _utc_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_row(row, now: datetime, contract: dict) -> dict:
    """Normalize one row, or raise a safe reason code without exposing values."""
    if not isinstance(row, dict):
        raise RowProblem("NOT_OBJECT")
    expected = set(contract["required_fields"])
    if expected - row.keys():
        raise RowProblem("SCHEMA_MISSING_FIELD")
    if row.keys() - expected:
        raise RowProblem("SCHEMA_DRIFT")
    event_id, region = row["event_id"], row["region_code"]
    if not isinstance(event_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", event_id):
        raise RowProblem("BAD_EVENT_ID")
    if not isinstance(region, str) or not re.fullmatch(r"[A-Z]{1,8}", region):
        raise RowProblem("BAD_REGION")
    magnitude = row["magnitude"]
    if magnitude is not None:
        if (isinstance(magnitude, bool) or not isinstance(magnitude, (int, float))
                or not math.isfinite(magnitude) or not -5 <= magnitude <= 12):
            raise RowProblem("BAD_MAGNITUDE")
    observed = _parse_time(row["observed_at"])
    updated = _parse_time(row["source_updated_at"])
    if updated < observed:
        raise RowProblem("UPDATE_BEFORE_EVENT")
    if observed > now + timedelta(minutes=contract["max_future_skew_minutes"]):
        raise RowProblem("FUTURE_TIMESTAMP")
    return {
        "event_id": event_id, "region_code": region,
        "observed_at": _utc_z(observed), "source_updated_at": _utc_z(updated),
        "magnitude": magnitude,
        "stale": now - observed > timedelta(hours=contract["max_freshness_hours"]),
    }


def _row_sha(row) -> str:
    """Store only a stable SHA-256 of the raw record, never its contents."""
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str,
                         separators=(",", ":")).encode("utf8")
    return hashlib.sha256(payload).hexdigest()


def assess_batch(rows: list, now: datetime, contract: dict) -> dict:
    if not isinstance(rows, list):
        raise TypeError("batch must be a list")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(timezone.utc)
    validated, quarantined, seen = [], [], set()
    for index, row in enumerate(rows):
        digest = _row_sha(row)
        try:
            record = validate_row(row, now, contract)
            if record["event_id"] in seen:
                raise RowProblem("DUPLICATE_EVENT")
            seen.add(record["event_id"])
            validated.append((index, record, digest))
        except RowProblem as error:
            quarantined.append((index, error.code, digest))
    total = len(rows)
    valid = len(validated)
    complete = sum(r["magnitude"] is not None for _, r, _ in validated)
    stale = sum(r["stale"] for _, r, _ in validated)
    valid_ratio = valid / total if total else 0.0
    completeness = complete / valid if valid else 0.0
    stale_ratio = stale / valid if valid else 0.0
    problems = []
    if total == 0:
        problems.append("EMPTY_BATCH")
    if valid_ratio < contract["min_valid_ratio"]:
        problems.append("VALID_RATIO")
    if completeness < contract["min_magnitude_completeness"]:
        problems.append("COMPLETENESS")
    if stale_ratio > contract["max_stale_ratio"]:
        problems.append("FRESHNESS")
    return {
        "total_rows": total, "valid_rows": valid,
        "quarantined_rows": len(quarantined), "stale_rows": stale,
        "magnitude_completeness": round(completeness, 6),
        "valid_ratio": round(valid_ratio, 6),
        "stale_ratio": round(stale_ratio, 6),
        "passed": not problems, "issues": problems,
        "validated": validated, "quarantine": quarantined,
    }


def ensure_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
      create table if not exists curated_events (
        event_id text primary key,
        observed_at text not null,
        source_updated_at text not null,
        region_code text not null,
        magnitude real,
        source_sha256 text not null,
        contract_version text not null
      );
      create table if not exists quality_runs (
        run_id text primary key, contract_version text not null,
        total_rows integer not null, valid_rows integer not null,
        quarantined_rows integer not null, stale_rows integer not null,
        published_rows integer not null,
        status text not null check(status in ('passed', 'blocked')),
        issue_codes text not null
      );
      create table if not exists quarantine_records (
        run_id text not null references quality_runs(run_id),
        row_index integer not null, reason_code text not null,
        payload_sha256 text not null check(length(payload_sha256)=64),
        primary key(run_id, row_index)
      );
      create table if not exists lineage_records (
        run_id text not null references quality_runs(run_id),
        event_id text not null, source_sha256 text not null,
        contract_version text not null, was_applied integer not null
          check(was_applied in (0,1)),
        primary key(run_id, event_id)
      );
    """)


def process_batch(
    db: sqlite3.Connection, run_id: str, rows: list, now: datetime,
    contract: dict, *, simulate_crash: bool = False
) -> dict:
    """Atomically publish a quality-passing batch or block it with audit evidence.

    Reusing run_id is rejected. Failed quality checks persist run + quarantine
    but write NO curated data. Crash simulation rolls back the entire transaction.
    """
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", run_id):
        raise ValueError("run_id must be a short, safe identifier")
    if contract.get("schema_version") != VERSION:
        raise ValueError("unsupported data contract")
    if db.in_transaction:
        raise ValueError("finish the existing transaction before calling process_batch")
    assessment = assess_batch(rows, now, contract)
    ensure_schema(db)
    published = 0
    try:
        db.execute("begin immediate")
        if db.execute("select 1 from quality_runs where run_id=?", (run_id,)).fetchone():
            raise ValueError("run_id already exists")
        status = "passed" if assessment["passed"] else "blocked"
        db.execute("""
            insert into quality_runs(
                run_id, contract_version, total_rows, valid_rows,
                quarantined_rows, stale_rows, published_rows, status, issue_codes
            ) values(?,?,?,?,?,?,?,?,?)
        """, (
            run_id, VERSION, assessment["total_rows"], assessment["valid_rows"],
            assessment["quarantined_rows"], assessment["stale_rows"], 0,
            status, json.dumps(assessment["issues"])
        ))
        if assessment["passed"]:
            for _, event, digest in assessment["validated"]:
                cursor = db.execute("""
                    insert into curated_events(
                        event_id, observed_at, source_updated_at, region_code,
                        magnitude, source_sha256, contract_version
                    ) values(?,?,?,?,?,?,?)
                    on conflict(event_id) do update set
                        observed_at=excluded.observed_at,
                        source_updated_at=excluded.source_updated_at,
                        region_code=excluded.region_code,
                        magnitude=excluded.magnitude,
                        source_sha256=excluded.source_sha256,
                        contract_version=excluded.contract_version
                    where excluded.source_updated_at > curated_events.source_updated_at
                """, (
                    event["event_id"], event["observed_at"], event["source_updated_at"],
                    event["region_code"], event["magnitude"], digest, VERSION
                ))
                applied = int(cursor.rowcount == 1)
                published += applied
                db.execute("""
                    insert into lineage_records(
                        run_id, event_id, source_sha256, contract_version, was_applied
                    ) values(?,?,?,?,?)
                """, (run_id, event["event_id"], digest, VERSION, applied))
        db.execute("update quality_runs set published_rows=? where run_id=?", (published, run_id))
        for index, reason, digest in assessment["quarantine"]:
            db.execute("""
                insert into quarantine_records(run_id,row_index,reason_code,payload_sha256)
                values(?,?,?,?)
            """, (run_id, index, reason, digest))
        if simulate_crash:
            raise RuntimeError("simulated crash before atomic commit")
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {
        key: assessment[key] for key in (
            "total_rows", "valid_rows", "quarantined_rows", "stale_rows",
            "valid_ratio", "stale_ratio", "magnitude_completeness",
            "passed", "issues"
        )
    } | {"run_id": run_id, "status": status, "published_rows": published}


def lineage_order(graph: dict) -> list[str]:
    """Validate asset lineage, reject cycles and ensure source → serving path."""
    if not isinstance(graph, dict):
        raise ValueError("lineage must be an object")
    assets = graph.get("assets")
    edges = graph.get("edges")
    if (not isinstance(assets, list) or not isinstance(edges, list)
        or len(set(assets)) != len(assets) or
        not all(isinstance(x, str) and x for x in assets)):
        raise ValueError("invalid lineage assets")
    if "source_api" not in assets or "daily_metrics" not in assets:
        raise ValueError("lineage is missing required boundary assets")
    outgoing = {x: set() for x in assets}
    indegree = {x: 0 for x in assets}
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError("invalid lineage edge")
        src, target = edge
        if src not in outgoing or target not in outgoing:
            raise ValueError("lineage references missing asset")
        if target not in outgoing[src]:
            outgoing[src].add(target)
            indegree[target] += 1
    ready = []
    for name, degree in indegree.items():
        if degree == 0:
            heappush(ready, name)
    order = []
    while ready:
        name = heappop(ready)
        order.append(name)
        for target in outgoing[name]:
            indegree[target] -= 1
            if indegree[target] == 0:
                heappush(ready, target)
    if len(order) != len(assets):
        raise ValueError("lineage contains cycle")
    reached, todo = set(), ["source_api"]
    while todo:
        node = todo.pop()
        if node in reached:
            continue
        reached.add(node)
        todo.extend(outgoing[node])
    if "daily_metrics" not in reached:
        raise ValueError("serving asset disconnected from source")
    return order

