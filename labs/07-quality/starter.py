"""Stage 07 learner assignment. Implement functions by following README and grader.

Only use local Python and SQLite. Never store raw rejected payloads.
"""
class RowProblem(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def load_contract(path=None):
    raise NotImplementedError("Parse and validate contract version and quality thresholds")


def validate_row(row, now, contract):
    raise NotImplementedError("Validate row fields, types, bounds and timestamps")


def assess_batch(rows, now, contract):
    raise NotImplementedError("Quarantine invalid records, compute completeness/freshness")


def ensure_schema(db):
    raise NotImplementedError("Create curated, quality, quarantine and lineage tables")


def process_batch(db, run_id, rows, now, contract, *, simulate_crash=False):
    raise NotImplementedError("Quality gate and transactional publish + safe audit")


def lineage_order(graph):
    raise NotImplementedError("Validate lineage edges, cycles and source-to-serving path")

