
"""Stage 10 independent standard-library Map/Reduce correctness oracle.

Educational only: bounded in-memory input, SHA partition buckets, no real
parallel workers or cluster. A real PySpark DataFrame path is in spark_pipeline.py.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
import math
from pathlib import Path
import re

FIELDS = frozenset(("event_id", "observed_at", "source_updated_at",
                    "region_code", "magnitude"))
ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
REGION_PATTERN = re.compile(r"[A-Z]{1,8}\Z")


class InvalidRecord(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def check_partitions(partitions):
    if type(partitions) is not int or not 1 <= partitions <= 32:
        raise ValueError("partitions must be an integer between 1 and 32")


def parse_utc(value):
    if not isinstance(value, str):
        raise InvalidRecord("BAD_TIMESTAMP")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidRecord("BAD_TIMESTAMP") from exc
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise InvalidRecord("NAIVE_TIMESTAMP")
    return instant.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize(raw):
    if not isinstance(raw, dict):
        raise InvalidRecord("NOT_OBJECT")
    if set(raw) != FIELDS:
        raise InvalidRecord("SCHEMA_DRIFT")
    event_id, region = raw["event_id"], raw["region_code"]
    if not isinstance(event_id, str) or not ID_PATTERN.fullmatch(event_id):
        raise InvalidRecord("BAD_ID")
    if not isinstance(region, str) or not REGION_PATTERN.fullmatch(region):
        raise InvalidRecord("BAD_REGION")
    number = raw["magnitude"]
    if number is not None:
        if (type(number) not in (int, float) or not math.isfinite(number)
            or not -5 <= number <= 12):
            raise InvalidRecord("BAD_MAGNITUDE")
        number = float(number)
    observed, updated = parse_utc(raw["observed_at"]), parse_utc(raw["source_updated_at"])
    if updated < observed:
        raise InvalidRecord("UPDATE_BEFORE_OBSERVATION")
    row = {
        "event_id": event_id, "observed_utc": observed, "updated_utc": updated,
        "region_code": region, "magnitude": number,
    }
    row["digest"] = sha256(json.dumps(
        row, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf8")).hexdigest()
    return row


def read_jsonl(path: Path):
    """Return normalized records and safe (line-number, reason-code) quarantines."""
    accepted, rejected = [], []
    with Path(path).open("r", encoding="utf8") as source:
        for line_num, text in enumerate(source, start=1):
            if not text.strip():
                continue
            try:
                record = normalize(json.loads(text))
                accepted.append(record)
            except json.JSONDecodeError:
                rejected.append({"line": line_num, "reason": "BAD_JSON"})
            except InvalidRecord as exc:
                rejected.append({"line": line_num, "reason": exc.reason})
    return accepted, rejected


def partition_for(event_id, partitions):
    """Stable, deterministic mapper assignment. Builtin hash() is process-randomized."""
    check_partitions(partitions)
    return int.from_bytes(sha256(event_id.encode("utf8")).digest()[:8], "big") % partitions


def select_latest(records, partitions):
    """Simulate keyed partition+reduce, keeping latest revision per event ID."""
    check_partitions(partitions)
    buckets = [dict() for _ in range(partitions)]
    for row in records:
        slot = buckets[partition_for(row["event_id"], partitions)]
        prior = slot.get(row["event_id"])
        if prior is None or (row["updated_utc"], row["digest"]) > (
            prior["updated_utc"], prior["digest"]
        ):
            slot[row["event_id"]] = row
    return [value for slot in buckets for value in slot.values()]


def summarize(selected):
    groups = defaultdict(list)
    for row in selected:
        groups[(row["observed_utc"][:10], row["region_code"])].append(row["magnitude"])
    result = []
    for (day, region), measures in sorted(groups.items()):
        known = [Decimal(str(v)) for v in measures if v is not None]
        average = (float((sum(known) / Decimal(len(known))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )) if known else None)
        result.append({
            "day_utc": day, "region_code": region, "total_events": len(measures),
            "known_magnitude_events": len(known), "average_magnitude": average,
        })
    return result


def run_light(path, partitions=2):
    """One reproducible, intentionally small dataset. Not a parallel benchmark."""
    rows, rejected = read_jsonl(path)
    latest = select_latest(rows, partitions)
    return {
        "input_rows": len(rows) + len(rejected),
        "valid_rows": len(rows),
        "rejected_rows": len(rejected),
        "rejected_reasons": sorted(item["reason"] for item in rejected),
        "deduplicated_events": len(latest),
        "duplicates_removed": len(rows) - len(latest),
        "metrics": summarize(latest),
    }


def expected_snapshot():
    """Independent hard-coded oracle for the provided synthetic fixture."""
    return {
        "input_rows": 16, "valid_rows": 12, "rejected_rows": 4,
        "rejected_reasons": ["BAD_MAGNITUDE", "BAD_REGION", "NAIVE_TIMESTAMP", "SCHEMA_DRIFT"],
        "deduplicated_events": 9, "duplicates_removed": 3,
        "metrics": [
            {"day_utc": "2026-01-01", "region_code": "E", "total_events": 2,
             "known_magnitude_events": 1, "average_magnitude": 4.4},
            {"day_utc": "2026-01-01", "region_code": "N", "total_events": 2,
             "known_magnitude_events": 2, "average_magnitude": 2.25},
            {"day_utc": "2026-01-02", "region_code": "E", "total_events": 1,
             "known_magnitude_events": 1, "average_magnitude": 5.7},
            {"day_utc": "2026-01-02", "region_code": "N", "total_events": 1,
             "known_magnitude_events": 1, "average_magnitude": 2.2},
            {"day_utc": "2026-01-02", "region_code": "W", "total_events": 2,
             "known_magnitude_events": 1, "average_magnitude": 0.6},
            {"day_utc": "2026-01-03", "region_code": "S", "total_events": 1,
             "known_magnitude_events": 0, "average_magnitude": None},
        ],
    }
