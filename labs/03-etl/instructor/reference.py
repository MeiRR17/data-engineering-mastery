"""Deterministic SQLite reference for CI. No network, no credentials."""
import hashlib
import json
import math
import re
from datetime import datetime, timezone

class DataQualityError(ValueError):
    pass


def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        observed_at TEXT NOT NULL,
        source_updated_at TEXT NOT NULL,
        magnitude REAL,
        place TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS quarantine (
        fingerprint TEXT NOT NULL,
        reason TEXT NOT NULL,
        PRIMARY KEY (fingerprint, reason)
    )""")
    conn.commit()


def iso(value):
    if not isinstance(value, str):
        raise DataQualityError("timestamp must be ISO text")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise DataQualityError("malformed timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise DataQualityError("timestamp must have timezone")
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds")


def clean(row):
    if not isinstance(row, dict):
        raise DataQualityError("row must be object")
    eid = row.get("event_id")
    if not isinstance(eid, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", eid):
        raise DataQualityError("invalid event_id")
    observed, updated = iso(row.get("observed_at")), iso(row.get("source_updated_at"))
    if updated < observed:
        raise DataQualityError("updated before observed")
    numbers = {}
    for key, lo, hi in (("magnitude", -5, 12), ("latitude", -90, 90), ("longitude", -180, 180)):
        value = row.get(key)
        if key == "magnitude" and value is None:
            numbers[key] = None
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not lo <= value <= hi:
            raise DataQualityError(f"invalid {key}")
        numbers[key] = float(value)
    place = row.get("place")
    if not isinstance(place, str) or not place:
        raise DataQualityError("invalid place")
    return eid, observed, updated, numbers["magnitude"], place[:300], numbers["latitude"], numbers["longitude"]


def load_batch(conn, events, max_reject_fraction=0.5, fail_after=None):
    if not isinstance(events, list):
        raise DataQualityError("events must be a list")
    if isinstance(max_reject_fraction, bool) or not isinstance(max_reject_fraction, (int,float)) or not 0 <= max_reject_fraction <= 1:
        raise ValueError("max_reject_fraction must be between 0 and 1")
    if fail_after is not None and (not isinstance(fail_after, int) or fail_after < 0):
        raise ValueError("fail_after must be a non-negative int")
    clean_rows, invalid = [], []
    for item in events:
        try:
            clean_rows.append(clean(item))
        except DataQualityError as exc:
            # Store no source payload or personal data in quarantine.
            fingerprint = hashlib.sha256(json.dumps(item, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")).hexdigest()
            invalid.append((fingerprint, str(exc)))
    if events and len(invalid) / len(events) > max_reject_fraction:
        raise DataQualityError("batch exceeds rejected record threshold; no writes committed")
    counters = {"written": 0, "rejected": len(invalid), "unchanged": 0}
    with conn:
        for idx, row in enumerate(clean_rows):
            previous = conn.total_changes
            conn.execute("""INSERT INTO events
                (event_id,observed_at,source_updated_at,magnitude,place,latitude,longitude)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(event_id) DO UPDATE SET
                  observed_at=excluded.observed_at,
                  source_updated_at=excluded.source_updated_at,
                  magnitude=excluded.magnitude,
                  place=excluded.place,
                  latitude=excluded.latitude,
                  longitude=excluded.longitude
                WHERE excluded.source_updated_at > events.source_updated_at""", row)
            if conn.total_changes > previous:
                counters["written"] += 1
            else:
                counters["unchanged"] += 1
            if fail_after is not None and idx == fail_after:
                raise RuntimeError("injected crash during transaction")
        for fingerprint, reason in invalid:
            conn.execute("INSERT OR IGNORE INTO quarantine(fingerprint,reason) VALUES(?,?)", (fingerprint, reason))
    return counters
