#!/usr/bin/env python3
"""Offline CSV contract drift audit: aggregates only, no raw data retained."""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys
from collections import Counter


MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100_000
MAX_COLUMNS = 100
MAX_FIELD_BYTES = 256 * 1024
INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
ISO_TIMESTAMP = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})?\Z"
)
KINDS = ("boolean", "integer", "decimal", "date", "timestamp", "text")


class AuditInputError(ValueError):
    """The files cannot be safely or unambiguously assessed."""


def value_kind(value: str) -> str:
    """Infer one conservative, exact scalar kind; do not coerce source values."""
    stripped = value.strip()
    if stripped.casefold() in ("true", "false"):
        return "boolean"
    if INTEGER.fullmatch(stripped):
        return "integer"
    if NUMBER.fullmatch(stripped):
        try:
            if Decimal(stripped).is_finite():
                return "decimal"
        except InvalidOperation:
            pass
        return "text"
    if ISO_DATE.fullmatch(stripped):
        try:
            date.fromisoformat(stripped)
            return "date"
        except ValueError:
            pass
    if ISO_TIMESTAMP.fullmatch(stripped):
        try:
            datetime.fromisoformat(stripped.replace("Z", "+00:00"))
            return "timestamp"
        except ValueError:
            pass
    return "text"


def dominant_kind(counter: Counter[str]) -> str:
    """Report mixed domains as text rather than guessing a majority type."""
    present = set(counter)
    if not present:
        return "empty"
    if present <= {"integer", "decimal"}:
        return "decimal" if "decimal" in present else "integer"
    return next(iter(present)) if len(present) == 1 else "mixed"


def profile_csv(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise AuditInputError("Input must be an existing regular non-symlink CSV file")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise AuditInputError(f"CSV exceeds {MAX_FILE_BYTES // 1024 // 1024} MiB limit")
    columns: list[str] = []
    nonempty: list[Counter[str]] = []
    missing: list[int] = []
    rows = 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            csv.field_size_limit(MAX_FIELD_BYTES)
            reader = csv.reader(handle, strict=True)
            header = next(reader, None)
            if not header:
                raise AuditInputError("CSV must contain a nonempty header row")
            if len(header) > MAX_COLUMNS:
                raise AuditInputError(f"More than {MAX_COLUMNS} columns")
            if any(not name.strip() or name != name.strip() for name in header):
                raise AuditInputError("Column headers must be nonblank and trimmed")
            if any(len(name) > 160 or any(ord(char) < 32 for char in name)
                   for name in header):
                raise AuditInputError("Column header contains control characters or is too long")
            if len(header) != len(set(header)):
                raise AuditInputError("Duplicate CSV column headers")
            columns = header
            nonempty = [Counter() for _ in header]
            missing = [0 for _ in header]
            for record in reader:
                rows += 1
                if rows > MAX_ROWS:
                    raise AuditInputError(f"CSV exceeds {MAX_ROWS} data rows")
                if len(record) != len(header):
                    raise AuditInputError(
                        f"Row {rows + 1} has {len(record)} values, expected {len(header)}"
                    )
                for index, value in enumerate(record):
                    if not value.strip():
                        missing[index] += 1
                    else:
                        nonempty[index][value_kind(value)] += 1
    except (OSError, UnicodeError, csv.Error) as exc:
        raise AuditInputError(f"Cannot parse UTF-8 CSV: {type(exc).__name__}") from exc
    if rows == 0:
        raise AuditInputError("CSV has a header but no data rows; drift cannot be inferred")
    return {
        "rows": rows,
        "columns": {
            name: {
                "kind": dominant_kind(nonempty[index]),
                "missing": missing[index],
                "missing_rate": round(missing[index] / rows, 6),
                "nonempty_kind_counts": {
                    kind: nonempty[index][kind]
                    for kind in KINDS if nonempty[index][kind] > 0
                },
            }
            for index, name in enumerate(columns)
        },
        "column_order": columns,
    }


def compare(baseline: dict, candidate: dict, threshold: float,
            strict_additions: bool = False) -> dict:
    old = baseline["columns"]
    new = candidate["columns"]
    findings: list[dict] = []

    def add(severity: str, rule: str, column: str, description: str) -> None:
        findings.append({
            "severity": severity,
            "rule": rule,
            "column": column,
            "description": description,
        })

    for column in baseline["column_order"]:
        if column not in new:
            add("breaking", "removed_column", column,
                "A baseline column is absent in the candidate")
            continue
        before, after = old[column], new[column]
        old_kind, new_kind = before["kind"], after["kind"]
        if old_kind != new_kind:
            if old_kind == "integer" and new_kind == "decimal":
                add("info", "numeric_widening", column,
                    "Integer values widened to decimal; review downstream contracts")
            elif "empty" in (old_kind, new_kind) or "mixed" in (old_kind, new_kind):
                add("warning", "ambiguous_type_change", column,
                    f"Inferred kind changed from {old_kind} to {new_kind}")
            else:
                add("breaking", "type_change", column,
                    f"Inferred kind changed from {old_kind} to {new_kind}")
        increase = after["missing_rate"] - before["missing_rate"]
        if increase > threshold + 1e-9:
            add("warning", "missingness_increase", column,
                f"Missing fraction rose by {increase:.4f}, above threshold {threshold:.4f}")

    for column in candidate["column_order"]:
        if column not in old:
            add("breaking" if strict_additions else "warning", "added_column", column,
                "Candidate contains a column not in the baseline")

    shared_old_order = [name for name in baseline["column_order"] if name in new]
    shared_new_order = [name for name in candidate["column_order"] if name in old]
    if shared_old_order != shared_new_order:
        add("warning", "column_order_change", "(shared columns)",
            "Shared columns changed order; position-based CSV readers may break")

    count = Counter(entry["severity"] for entry in findings)
    return {
        "schema_version": 1,
        "input_kind": "local_csv_aggregate_profiles_only",
        "baseline_row_count": baseline["rows"],
        "candidate_row_count": candidate["rows"],
        "baseline_column_count": len(old),
        "candidate_column_count": len(new),
        "max_missingness_increase": threshold,
        "strict_additions": strict_additions,
        "status": "breaking" if count["breaking"] else
                  "warning" if count["warning"] else "compatible_under_these_rules",
        "finding_counts": {key: count[key] for key in ("breaking", "warning", "info")},
        "findings": findings,
        "baseline": baseline,
        "candidate": candidate,
        "notice": (
            "Statistical type inference is not a declared schema contract. "
            "This report does not prove semantic correctness, freshness, provenance, "
            "lack of personal data, or safe publication."
        ),
    }


def markdown(report: dict) -> str:
    lines = [
        "# Offline CSV schema drift audit",
        "",
        f"**Status:** {report['status']}",
        f"**Rows:** baseline {report['baseline_row_count']} / candidate {report['candidate_row_count']}",
        f"**Columns:** baseline {report['baseline_column_count']} / candidate {report['candidate_column_count']}",
        "",
        "| Severity | Rule | Column | Observation |",
        "| --- | --- | --- | --- |",
    ]
    for f in report["findings"]:
        description = f["description"].replace("|", r"\|")
        column = (f["column"].replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace("|", r"\|")
                  .replace("\n", " "))
        lines.append(
            f"| {f['severity']} | {f['rule']} | {column} | {description} |"
        )
    if not report["findings"]:
        lines.append("| info | no_detected_change | — | No drift under these audit rules |")
    lines.extend(["", report["notice"]])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--max-missing-increase", type=float, default=0.10)
    parser.add_argument("--strict-additions", action="store_true")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args(argv)
    threshold = args.max_missing_increase
    if not (0 <= threshold <= 1):
        parser.error("--max-missing-increase must be between 0 and 1")
    try:
        baseline, candidate = profile_csv(args.baseline), profile_csv(args.candidate)
        report = compare(baseline, candidate, threshold, args.strict_additions)
    except AuditInputError as exc:
        print(f"CSV audit rejected: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(markdown(report))
    if report["status"] == "breaking":
        return 1
    if args.fail_on_warning and report["status"] == "warning":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
