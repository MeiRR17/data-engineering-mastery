#!/usr/bin/env python3
"""Offline SQLite semantic grader; intentionally rejects unsafe SQL statements."""
from __future__ import annotations
import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = ("duplicates", "latest", "daily", "strongest")


def split_tasks(text: str):
    blocks = {}
    for match in re.finditer(r"(?im)^-- task: ([a-z]+)\s*$", text):
        end = re.search(r"(?im)^-- task: [a-z]+\s*$", text[match.end():])
        sql = text[match.end(): match.end() + end.start() if end else len(text)].strip()
        if match.group(1) in blocks:
            raise ValueError(f"duplicate task {match.group(1)}")
        # Only read queries; SQLite authorizer blocks mutation too.
        sql_no_comments = re.sub(r"--[^\n]*", "", sql).strip().rstrip(";").strip()
        if not re.match(r"(?is)^(WITH\b|SELECT\b)", sql_no_comments):
            raise ValueError(f"{match.group(1)} must be a SELECT or WITH query")
        blocks[match.group(1)] = sql_no_comments
    if set(blocks) != set(TASKS):
        raise ValueError(f"expected tasks {TASKS}, found {tuple(blocks)}")
    return blocks


def database(extra: bool):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
    if extra:
        db.executemany("INSERT INTO quake_events(event_id,location,occurred_on,magnitude,updated_at) VALUES(?,?,?,?,?)", [
            ("e4", "Island A", "2026-01-03", None, "2026-01-04T00:00:00Z"),
            ("e3", "Island A", "2026-01-02", 4.7, "2026-01-04T00:00:00Z"),
            ("e5", "Island C", "2026-01-03", 2.2, "2026-01-04T00:00:00Z"),
            ("e5", "Island C", "2026-01-03", 2.6, "2026-01-04T00:00:00Z"),
        ])
    # Deny mutation, virtual tables, ATTACH, pragmas and external side effects.
    forbidden = {sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
                 sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_ALTER_TABLE,
                 sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_PRAGMA,
                 sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_DROP_INDEX}
    def authorize(action, _arg1, _arg2, _db, _trigger):
        return sqlite3.SQLITE_DENY if action in forbidden else sqlite3.SQLITE_OK
    db.set_authorizer(authorize)
    return db


def expected(extra):
    latest = [
        ("e1", "Island A", "2026-01-01", 3.5, "2026-01-02T00:00:00Z"),
        ("e2", "Island B", "2026-01-01", 4.2, "2026-01-02T02:00:00Z"),
        ("e3", "Island A", "2026-01-02", 4.7 if extra else 4.0,
         "2026-01-04T00:00:00Z" if extra else "2026-01-03T00:00:00Z"),
    ]
    if extra:
        latest += [("e4", "Island A", "2026-01-03", None, "2026-01-04T00:00:00Z"),
                   ("e5", "Island C", "2026-01-03", 2.6, "2026-01-04T00:00:00Z")]
    return {
        "duplicates": [("e2", 2)] + ([("e3", 2), ("e5", 2)] if extra else []),
        "latest": latest,
        "daily": [("2026-01-01", 2, 3.85), ("2026-01-02", 1, 4.7 if extra else 4.0)] +
                 ([("2026-01-03", 2, 2.6)] if extra else []),
        "strongest": [("Island A", "e3", 4.7 if extra else 4.0), ("Island B", "e2", 4.2)] +
                     ([("Island C", "e5", 2.6)] if extra else []),
    }


def check(sql_path):
    blocks = split_tasks(sql_path.read_text(encoding="utf-8"))
    errors = []
    for extra in (False, True):
        conn = database(extra)
        baseline = expected(extra)
        for name, sql in blocks.items():
            try:
                observed = [tuple(row) for row in conn.execute(sql)]
                if Counter(observed) != Counter(baseline[name]):
                    errors.append(f"{name} ({'extended' if extra else 'baseline'}): expected {baseline[name]}, observed {observed[:8]}")
            except sqlite3.Error as exc:
                errors.append(f"{name}: SQL error: {exc}")
        conn.close()
    return errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", action="store_true", help="maintainer regression test; read reference only after attempting")
    args = ap.parse_args()
    path = HERE / ("instructor/reference.sql" if args.reference else "tasks.sql")
    failures = check(path)
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        raise SystemExit(1)
    print("PASS: 4 SQL tasks x 2 datasets (baseline and unseen extra cases).")
