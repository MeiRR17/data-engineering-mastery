"""Instructor reference for a deterministic, local Stage 06 pipeline.

The SQLite run journal is persisted alongside loaded records in one transaction.
A replay after a lost acknowledgement is skipped; force=True performs a backfill.
No external services, telemetry or credentials are used.
"""
from __future__ import annotations

from datetime import date, timedelta
from heapq import heappop, heappush
import sqlite3


class TransientSourceError(RuntimeError):
    """Retryable failure of a synthetic upstream provider."""


class AcknowledgementLost(RuntimeError):
    """The database committed, but the caller did not receive confirmation."""


def dag_order(dependencies: dict[str, tuple[str, ...]]) -> list[str]:
    """Produce deterministic topological order; reject missing nodes and cycles."""
    nodes = set(dependencies)
    if any(dep not in nodes for deps in dependencies.values() for dep in deps):
        raise ValueError("unknown DAG dependency")
    outgoing = {name: [] for name in dependencies}
    indegree = {name: len(set(deps)) for name, deps in dependencies.items()}
    for name, deps in dependencies.items():
        for dep in set(deps):
            outgoing[dep].append(name)
    ready = []
    for name, count in indegree.items():
        if count == 0:
            heappush(ready, name)
    ordered = []
    while ready:
        name = heappop(ready)
        ordered.append(name)
        for child in outgoing[name]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heappush(ready, child)
    if len(ordered) != len(nodes):
        raise ValueError("DAG contains a cycle")
    return ordered


def backfill_days(start: str, end: str, maximum: int = 31) -> list[str]:
    """Return inclusive calendar days, rejecting unbounded/reversed backfills."""
    try:
        a, b = date.fromisoformat(start), date.fromisoformat(end)
    except (TypeError, ValueError) as exc:
        raise ValueError("dates must use ISO YYYY-MM-DD") from exc
    if a.isoformat() != start or b.isoformat() != end:
        raise ValueError("dates must be exact ISO YYYY-MM-DD")
    span = (b - a).days + 1
    if span < 1 or span > maximum or maximum < 1:
        raise ValueError("backfill window out of bounds")
    return [(a + timedelta(days=i)).isoformat() for i in range(span)]


def ensure_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
    create table if not exists curated_events(
      event_id text primary key,
      event_day text not null,
      magnitude real,
      source_updated integer not null
    );
    create table if not exists pipeline_runs(
      event_day text primary key,
      status text not null check(status in ('success','failed')),
      attempts integer not null check(attempts >= 1),
      submitted_rows integer not null check(submitted_rows >= 0),
      last_error text
    );
    """)


def _validated(event: dict, expected_day: str) -> tuple:
    """Validate the entire batch within the same database transaction."""
    if not isinstance(event, dict):
        raise ValueError("row is not an object")
    event_id = event.get("event_id")
    day = event.get("event_day")
    updated = event.get("source_updated")
    mag = event.get("magnitude")
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("missing event_id")
    if day != expected_day:
        raise ValueError("event belongs to another day")
    if isinstance(updated, bool) or not isinstance(updated, int) or updated < 0:
        raise ValueError("invalid source_updated")
    if mag is not None and (
        isinstance(mag, bool) or not isinstance(mag, (int, float))
        or not -5 <= mag <= 12
    ):
        raise ValueError("invalid magnitude")
    return (event_id, day, mag, updated)


def ingest_day(db: sqlite3.Connection, day: str, provider, *,
               attempts: int = 3, force: bool = False,
               lose_ack: bool = False) -> dict:
    """Fetch, validate, idempotently load and checkpoint one day.

    provider(day) may raise TransientSourceError. No network/retry sleeps.
    On invalid batches all event writes roll back; an independent failure
    journal is recorded after the rollback. A force-backfill rechecks a day.
    """
    backfill_days(day, day)
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 1 or attempts > 10:
        raise ValueError("attempts must be 1..10")
    ensure_schema(db)
    prior = db.execute(
        "select status from pipeline_runs where event_day=?", (day,)
    ).fetchone()
    if prior and prior[0] == "success" and not force:
        return {"status": "skipped", "attempts": 0, "submitted_rows": 0}

    for attempt in range(1, attempts + 1):
        try:
            batch = provider(day)
        except TransientSourceError:
            if attempt == attempts:
                db.execute("""
                    insert into pipeline_runs(event_day,status,attempts,submitted_rows,last_error)
                    values(?,'failed',?,0,'transient source exhausted')
                    on conflict(event_day) do update set
                    status=excluded.status, attempts=excluded.attempts,
                    submitted_rows=0, last_error=excluded.last_error
                """, (day, attempt))
                db.commit()
                raise
            continue

        if not isinstance(batch, list):
            raise ValueError("provider must return a list")
        try:
            db.execute("begin immediate")
            for event in batch:
                row = _validated(event, day)
                db.execute("""
                    insert into curated_events(event_id,event_day,magnitude,source_updated)
                    values(?,?,?,?)
                    on conflict(event_id) do update set
                      event_day=excluded.event_day,
                      magnitude=excluded.magnitude,
                      source_updated=excluded.source_updated
                    where excluded.source_updated > curated_events.source_updated
                """, row)
            db.execute("""
                insert into pipeline_runs(event_day,status,attempts,submitted_rows,last_error)
                values(?,'success',?,?,null)
                on conflict(event_day) do update set
                  status=excluded.status, attempts=excluded.attempts,
                  submitted_rows=excluded.submitted_rows, last_error=null
            """, (day, attempt, len(batch)))
            db.commit()
        except Exception:
            db.rollback()
            db.execute("""
                insert into pipeline_runs(event_day,status,attempts,submitted_rows,last_error)
                values(?,'failed',?,0,'validation or database error')
                on conflict(event_day) do update set status='failed',
                    attempts=excluded.attempts, submitted_rows=0,
                    last_error=excluded.last_error
            """, (day, attempt))
            db.commit()
            raise
        if lose_ack:
            raise AcknowledgementLost("commit succeeded; acknowledgement was lost")
        return {"status": "success", "attempts": attempt, "submitted_rows": len(batch)}

    raise AssertionError("unreachable")

