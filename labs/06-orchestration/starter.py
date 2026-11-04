"""Learner starter. Complete the functions after attempting the exercises.

Do not copy the reference. Work from the contract and failing tests.
"""
class TransientSourceError(RuntimeError):
    pass

class AcknowledgementLost(RuntimeError):
    pass

def dag_order(dependencies):
    """Return a safe deterministic topological ordering; reject cycles."""
    raise NotImplementedError("Implement DAG dependency resolution")

def backfill_days(start, end, maximum=31):
    """Inclusive ISO date window with range safety checks."""
    raise NotImplementedError("Implement safe date backfill planning")

def ensure_schema(db):
    """Create curated_events and pipeline_runs tables in local SQLite."""
    raise NotImplementedError("Implement SQLite schema")

def ingest_day(db, day, provider, *, attempts=3, force=False, lose_ack=False):
    """Retry, validate, upsert and atomically checkpoint one day."""
    raise NotImplementedError("Implement durable orchestration")

