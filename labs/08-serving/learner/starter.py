"""Stage 08 extension: create an allowlisted, read-only region metrics report.

Input: path to an already-populated Stage 07 SQLite database and 1..20 limit.
Output: {"dataset": "synthetic-training", "items": [...], "limit": <limit>}

Each item: {region_code, total_events, known_magnitude_events, average_magnitude}.
Order by total_events descending, then region_code ascending.
Compute AVG using only non-NULL values; if all NULL return None.
Do not write to the source file or expose event IDs, hashes or payloads.
"""
from pathlib import Path


def region_summary(database: Path, limit: int = 10) -> dict:
    raise NotImplementedError("Implement the read-only regional aggregation")

