"""Create a disposable, synthetic Stage 08 database from the Stage 07 oracle."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
STAGE07 = ROOT / "labs/07-quality"
LAB_CLOCK = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)


def load_stage07():
    spec = spec_from_file_location("stage07_demo_reference", STAGE07 / "instructor/reference.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_demo_database(path: Path):
    """Use only a newly created temporary file; never overwrite real learner data."""
    path = Path(path)
    if path.exists():
        raise FileExistsError("refusing to overwrite an existing database")
    path.parent.mkdir(parents=True, exist_ok=True)
    oracle = load_stage07()
    rows = json.loads((STAGE07 / "data/synthetic_events.json").read_text(encoding="utf8"))
    contract = oracle.load_contract()
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        accepted = oracle.process_batch(db, "accepted-demo", rows, LAB_CLOCK, contract)
        if not accepted["passed"] or accepted["published_rows"] != 4:
            raise RuntimeError("expected synthetic good batch did not publish")
        invalid = deepcopy(rows)
        invalid[0]["unexpected_schema_field"] = "changed-upstream"
        blocked = oracle.process_batch(db, "blocked-demo", invalid, LAB_CLOCK, contract)
        if blocked["passed"] or blocked["published_rows"] != 0:
            raise RuntimeError("expected quality gate did not block the sample")
    return path

