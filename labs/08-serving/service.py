"""Stage 08 read-only analytics query service and guarded HTTP handler.

Only allowlisted SELECT statements run against a SQLite connection opened in
read-only mode. Source payloads, row digests and private tables are never served.
The handler serves only a small allowlisted web directory on localhost.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlsplit

LAB = Path(__file__).resolve().parent
MAX_LIMIT = 50
MAX_OFFSET = 1000
FRESHNESS_HOURS = 48
PUBLIC_FIELDS = ("event_id", "observed_at", "region_code", "magnitude")


def _limit(query: dict, *, default: int, allowed: set[str]) -> tuple[int, int]:
    if set(query) - allowed or any(len(values) != 1 for values in query.values()):
        raise ValueError("invalid query parameters")
    limit = query.get("limit", [str(default)])[0]
    offset = query.get("offset", ["0"])[0]
    if not limit.isascii() or not limit.isdecimal() or not 1 <= int(limit) <= MAX_LIMIT:
        raise ValueError("limit must be in 1..50")
    if not offset.isascii() or not offset.isdecimal() or int(offset) > MAX_OFFSET:
        raise ValueError("offset must be in 0..1000")
    return int(limit), int(offset)


class AnalyticsService:
    def __init__(self, database: Path, clock=None):
        self.database = Path(database).resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _connect(self):
        conn = sqlite3.connect(self.database.as_uri() + "?mode=ro", uri=True, timeout=2)
        conn.execute("PRAGMA query_only=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def health(self):
        with closing(self._connect()) as db:
            db.execute("SELECT count(*) FROM curated_events").fetchone()
        return {"status": "ok", "dataset": "synthetic-training"}

    def overview(self):
        with closing(self._connect()) as db:
            data = db.execute("""
                SELECT count(*) AS total_events,
                       count(magnitude) AS known_magnitude_events,
                       avg(magnitude) AS average_magnitude,
                       max(observed_at) AS latest_event_at
                FROM curated_events
            """).fetchone()
            latest_quality = db.execute("""
                SELECT status, valid_rows, quarantined_rows, published_rows
                FROM quality_runs ORDER BY rowid DESC LIMIT 1
            """).fetchone()
        observed = data["latest_event_at"]
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("clock must be timezone-aware")
        age = None
        state = "empty"
        if observed is not None:
            instant = datetime.fromisoformat(observed.replace("Z", "+00:00"))
            age = round((now.astimezone(timezone.utc) - instant).total_seconds() / 3600, 2)
            state = "future" if age < -5 / 60 else ("stale" if age > FRESHNESS_HOURS else "fresh")
        return {
            "dataset": "synthetic-training",
            "total_events": data["total_events"],
            "known_magnitude_events": data["known_magnitude_events"],
            "average_magnitude": round(data["average_magnitude"], 2)
                if data["average_magnitude"] is not None else None,
            "latest_event_at": observed,
            "age_hours": age,
            "freshness_status": state,
            "freshness_limit_hours": FRESHNESS_HOURS,
            "last_quality_status": latest_quality["status"] if latest_quality else "unknown",
            "last_quality_valid_rows": latest_quality["valid_rows"] if latest_quality else 0,
            "last_quality_rejected_rows": latest_quality["quarantined_rows"] if latest_quality else 0,
        }

    def daily(self, query):
        limit, _ = _limit(query, default=14, allowed={"limit"})
        if "offset" in query:
            raise ValueError("unsupported offset")
        with closing(self._connect()) as db:
            rows = db.execute("""
                SELECT substr(observed_at,1,10) AS day_utc,
                       count(*) AS total_events,
                       count(magnitude) AS known_magnitude_events,
                       round(avg(magnitude),2) AS average_magnitude
                FROM curated_events
                GROUP BY substr(observed_at,1,10)
                ORDER BY day_utc DESC LIMIT ?
            """, (limit,)).fetchall()
        return {"dataset": "synthetic-training", "items": [dict(row) for row in rows]}

    def events(self, query):
        limit, offset = _limit(query, default=20, allowed={"limit", "offset"})
        with closing(self._connect()) as db:
            rows = db.execute("""
                SELECT event_id, observed_at, region_code, magnitude
                FROM curated_events
                ORDER BY observed_at DESC, event_id ASC
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        return {"dataset": "synthetic-training", "items": [dict(row) for row in rows],
                "limit": limit, "offset": offset}

    def quality(self, query):
        limit, _ = _limit(query, default=10, allowed={"limit"})
        if "offset" in query:
            raise ValueError("unsupported offset")
        with closing(self._connect()) as db:
            rows = db.execute("""
                SELECT run_id, status, valid_rows, quarantined_rows, stale_rows,
                       published_rows, issue_codes
                FROM quality_runs ORDER BY rowid DESC LIMIT ?
            """, (limit,)).fetchall()
        # No raw payloads, full exception messages, digests, or secrets leave the API.
        return {
            "dataset": "synthetic-training",
            "items": [
                {"run_id": row["run_id"], "status": row["status"],
                 "valid_rows": row["valid_rows"],
                 "quarantined_rows": row["quarantined_rows"],
                 "stale_rows": row["stale_rows"],
                 "published_rows": row["published_rows"],
                 "issue_codes": json.loads(row["issue_codes"])}
                for row in rows
            ],
        }


def make_handler(database: Path, clock=None):
    """Create a strict localhost HTTP handler; unit tests can inject a fixed clock."""
    api = AnalyticsService(database, clock=clock)
    static_files = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/index.html": ("index.html", "text/html; charset=utf-8"),
        "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format, *args):
            # Avoid logging untrusted URLs, query parameters, or event payloads.
            pass

        def _response(self, status: int, content: bytes, kind: str):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self'; base-uri 'none'; "
                "form-action 'none'; frame-ancestors 'none'"
            )
            self.end_headers()
            self.wfile.write(content)

        def _json(self, status: int, payload: dict):
            self._response(status, json.dumps(payload, ensure_ascii=False,
                                              allow_nan=False).encode("utf-8"),
                           "application/json; charset=utf-8")

        def do_GET(self):
            try:
                if len(self.path) > 300:
                    raise ValueError("oversized URL")
                request = urlsplit(self.path)
                if request.fragment:
                    raise ValueError("unexpected fragment")
                if request.path in static_files:
                    if request.query:
                        raise ValueError("unexpected static query")
                    filename, kind = static_files[request.path]
                    self._response(200, (LAB / "web" / filename).read_bytes(), kind)
                    return
                if request.path not in {
                    "/api/v1/health", "/api/v1/overview", "/api/v1/daily",
                    "/api/v1/events", "/api/v1/quality"
                }:
                    self._json(404, {"error": "not found"})
                    return
                params = parse_qs(request.query, keep_blank_values=True, strict_parsing=True)
                if request.path == "/api/v1/health":
                    if params:
                        raise ValueError("health takes no parameters")
                    result = api.health()
                elif request.path == "/api/v1/overview":
                    if params:
                        raise ValueError("overview takes no parameters")
                    result = api.overview()
                elif request.path == "/api/v1/daily":
                    result = api.daily(params)
                elif request.path == "/api/v1/events":
                    result = api.events(params)
                else:
                    result = api.quality(params)
                self._json(200, result)
            except ValueError:
                self._json(400, {"error": "invalid request"})
            except (sqlite3.Error, OSError):
                self._json(503, {"error": "training dataset unavailable"})

        def _not_allowed(self):
            self.send_response(405)
            self.send_header("Allow", "GET")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()

        do_POST = _not_allowed
        do_PUT = _not_allowed
        do_PATCH = _not_allowed
        do_DELETE = _not_allowed
        do_HEAD = _not_allowed

    return Handler

