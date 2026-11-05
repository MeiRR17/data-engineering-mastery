"""Instructor-only oracle. Student should implement the starter independently."""
from contextlib import closing
from pathlib import Path
import sqlite3


def region_summary(database: Path, limit: int = 10) -> dict:
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer 1..20")
    path = Path(database).resolve()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        rows = db.execute("""
            SELECT region_code, count(*) AS total_events,
                   count(magnitude) AS known_magnitude_events,
                   round(avg(magnitude), 2) AS average_magnitude
            FROM curated_events
            GROUP BY region_code
            ORDER BY total_events DESC, region_code ASC
            LIMIT ?
        """, (limit,)).fetchall()
    return {
        "dataset": "synthetic-training",
        "items": [
            {"region_code": region, "total_events": count,
             "known_magnitude_events": known, "average_magnitude": mean}
            for region, count, known, mean in rows
        ],
        "limit": limit,
    }

