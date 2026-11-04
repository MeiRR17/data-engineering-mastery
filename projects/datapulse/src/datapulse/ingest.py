"""CLI entrypoint: fetch USGS GeoJSON, validate, and atomically ingest batches."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .client import SupabaseRestClient
from .etl import DataQualityError, transform_feed

USGS_FEEDS = {
    "hour": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
    "day": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
    "week": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson",
}


def fetch_feed(name: str) -> dict:
    req = urllib.request.Request(USGS_FEEDS[name], headers={"User-Agent": "DataPulse-Portfolio/1.0 (educational-project)", "Accept": "application/geo+json,application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=35) as response:
                if int(response.headers.get("Content-Length", "0") or "0") > 25_000_000:
                    raise ValueError("feed too large")
                body = response.read(25_000_001)
                if len(body) > 25_000_000:
                    raise ValueError("feed too large")
                return json.loads(body)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt == 2:
                raise RuntimeError("could not fetch USGS feed") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def run(feed: dict, *, client: SupabaseRestClient | None = None, name: str = "fixture", batch_size: int = 100) -> dict:
    rows, rejects = transform_feed(feed)
    fetched = len(feed["features"])
    # Do not silently accept a broken upstream schema or massive data loss.
    if fetched and len(rejects) / fetched > 0.25:
        raise DataQualityError(f"reject rate too high: {len(rejects)}/{fetched}")
    outcome = {"source_rows": fetched, "valid_rows": len(rows), "rejected_rows": len(rejects), "rejected_samples": rejects[:5], "loaded_rows": 0}
    if client is None:
        return outcome

    run_id = str(uuid.uuid4())
    client.start_run(run_id, name)
    try:
        for begin in range(0, len(rows), batch_size):
            outcome["loaded_rows"] += client.upload_batch(rows[begin:begin + batch_size])
        client.finish_run(run_id, status="success", source_rows=fetched, valid_rows=len(rows), rejected_rows=len(rejects), loaded_rows=outcome["loaded_rows"], finished_at=datetime.now(timezone.utc).isoformat())
    except Exception:
        client.finish_run(run_id, status="failed", source_rows=fetched, valid_rows=len(rows), rejected_rows=len(rejects), loaded_rows=outcome["loaded_rows"], finished_at=datetime.now(timezone.utc).isoformat())
        raise
    return outcome


def main() -> int:
    parser = argparse.ArgumentParser(description="DataPulse USGS → Supabase data pipeline")
    parser.add_argument("--feed", choices=USGS_FEEDS, default="day")
    parser.add_argument("--fixture", type=Path, help="read local GeoJSON instead of the public API")
    parser.add_argument("--dry-run", action="store_true", help="validate data but do not write to Supabase")
    args = parser.parse_args()
    try:
        feed = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture else fetch_feed(args.feed)
        client = None if args.dry_run else SupabaseRestClient(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])
        outcome = run(feed, client=client, name="fixture" if args.fixture else args.feed)
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, RuntimeError, urllib.error.URLError) as exc:
        print(f"DataPulse error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
