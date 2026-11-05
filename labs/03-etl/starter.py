"""Stage 03 learner starter: build transactional, replay-safe SQLite ingestion."""

class DataQualityError(ValueError):
    pass


def init_db(conn):
    """Create events and quarantine tables according to the README contract."""
    raise NotImplementedError("Define tables and constraints")


def load_batch(conn, events, max_reject_fraction=0.5, fail_after=None):
    """Atomically validate/load; return written/rejected/unchanged counters."""
    raise NotImplementedError("Build the ETL with idempotency, ordering and rollback")
