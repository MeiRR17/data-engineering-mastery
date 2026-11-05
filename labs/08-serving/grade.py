"""Stage 08 black-box API, freshness, safety, and dashboard asset tests.

All HTTP requests are made to an ephemeral loopback server backed by a
disposable synthetic SQLite fixture. No external network or cloud is used.
"""
from __future__ import annotations
from contextlib import closing

from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
import json
import sqlite3
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from demo import create_demo_database, load_stage07
from service import AnalyticsService, make_handler

LAB = Path(__file__).resolve().parent
FIXED_NOW = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)


def get(url, method="GET"):
    request = Request(url, method=method)
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except HTTPError as error:
        return error.code, dict(error.headers), error.read()


class Stage08ServingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix="stage08-tests-")
        cls.database = Path(cls.temp.name) / "fixture.sqlite"
        create_demo_database(cls.database)
        cls.service = AnalyticsService(cls.database, clock=lambda: FIXED_NOW)
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_handler(cls.database, clock=lambda: FIXED_NOW)
        )
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def api(self, path):
        status, headers, payload = get(self.base + path)
        return status, headers, json.loads(payload)

    def test_demo_fixture_has_good_and_blocked_quality_runs(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            self.assertEqual(db.execute("SELECT count(*) FROM curated_events").fetchone()[0], 4)
            self.assertEqual(db.execute("SELECT count(*) FROM quality_runs").fetchone()[0], 2)
            self.assertEqual(db.execute(
                "SELECT status FROM quality_runs ORDER BY rowid DESC LIMIT 1"
            ).fetchone()[0], "blocked")

    def test_overview_contract_and_known_mean(self):
        status, _, data = self.api("/api/v1/overview")
        self.assertEqual(status, 200)
        self.assertEqual(data["dataset"], "synthetic-training")
        self.assertEqual(data["total_events"], 4)
        self.assertEqual(data["known_magnitude_events"], 3)
        self.assertEqual(data["average_magnitude"], 2.87)
        self.assertEqual(data["last_quality_status"], "blocked")

    def test_freshness_is_time_aware(self):
        _, _, data = self.api("/api/v1/overview")
        self.assertEqual(data["freshness_status"], "fresh")
        self.assertEqual(data["age_hours"], 1.5)

    def test_stale_data_is_never_presented_as_fresh(self):
        service = AnalyticsService(
            self.database, clock=lambda: datetime(2026, 11, 5, tzinfo=timezone.utc)
        )
        data = service.overview()
        self.assertEqual(data["freshness_status"], "stale")
        self.assertGreater(data["age_hours"], data["freshness_limit_hours"])

    def test_quality_reports_blocked_reason_without_raw_payload(self):
        status, _, result = self.api("/api/v1/quality")
        self.assertEqual(status, 200)
        self.assertEqual(result["items"][0]["run_id"], "blocked-demo")
        self.assertEqual(result["items"][0]["status"], "blocked")
        self.assertEqual(result["items"][0]["published_rows"], 0)
        self.assertIn("COMPLETENESS", result["items"][0]["issue_codes"])
        self.assertEqual(result["items"][1]["status"], "passed")

    def test_daily_utc_counts_reconcile(self):
        status, _, data = self.api("/api/v1/daily")
        self.assertEqual(status, 200)
        self.assertEqual(data["items"], [
            {"day_utc": "2026-01-03", "total_events": 4,
             "known_magnitude_events": 3, "average_magnitude": 2.87}
        ])

    def test_event_pagination_limits_and_offset(self):
        status, _, first = self.api("/api/v1/events?limit=2&offset=0")
        self.assertEqual(status, 200)
        self.assertEqual(len(first["items"]), 2)
        self.assertEqual(first["items"][0]["event_id"], "lab-0704")
        status, _, second = self.api("/api/v1/events?limit=2&offset=2")
        self.assertEqual(status, 200)
        self.assertEqual(len(second["items"]), 2)
        ids = [x["event_id"] for x in first["items"] + second["items"]]
        self.assertEqual(len(set(ids)), 4)

    def test_events_are_explicitly_allowlisted(self):
        _, _, events = self.api("/api/v1/events")
        for row in events["items"]:
            self.assertEqual(set(row), {"event_id", "observed_at", "region_code", "magnitude"})

    def test_no_raw_payload_or_digest_in_any_public_json(self):
        for path in (
            "/api/v1/overview", "/api/v1/events", "/api/v1/daily", "/api/v1/quality"
        ):
            _, _, body = get(self.base + path)
            for forbidden in (
                b"source_sha256", b"payload_sha256", b"contract_version",
                b"source_updated_at", b"raw_payload", b"unexpected_schema_field",
                b"changed-upstream", b"quarantine_records", b"lineage_records",
            ):
                with self.subTest(path=path, forbidden=forbidden):
                    self.assertNotIn(forbidden, body)

    def test_bad_limit_is_rejected(self):
        for value in ["0", "51", "-1", "1.5", "1%20OR%201=1", ""]:
            status, _, body = self.api("/api/v1/events?limit=" + value)
            self.assertEqual(status, 400, (value, body))
            self.assertEqual(body["error"], "invalid request")

    def test_bad_offset_is_rejected(self):
        for value in ["-1", "1001", "1.2", "1%20UNION%20SELECT"]:
            status, _, _ = self.api("/api/v1/events?limit=2&offset=" + value)
            self.assertEqual(status, 400, value)

    def test_unknown_and_duplicate_query_parameters_are_rejected(self):
        for path in (
            "/api/v1/events?table=raw_earthquakes",
            "/api/v1/events?limit=1&limit=2",
            "/api/v1/daily?offset=1",
            "/api/v1/quality?offset=1",
            "/api/v1/events?limit",
        ):
            status, _, _ = self.api(path)
            self.assertEqual(status, 400, path)

    def test_health_is_public_but_not_configurable(self):
        status, _, data = self.api("/api/v1/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(self.api("/api/v1/health?sql=delete")[0], 400)

    def test_all_write_methods_are_denied(self):
        for method in ("POST", "PUT", "PATCH", "DELETE", "HEAD"):
            with self.subTest(method=method):
                status, headers, _ = get(self.base + "/api/v1/events", method=method)
                self.assertEqual(status, 405)
                self.assertEqual(headers.get("Allow"), "GET")

    def test_static_allowlist_only(self):
        for url, kind in (
            ("/", "text/html"), ("/index.html", "text/html"),
            ("/styles.css", "text/css"), ("/app.js", "text/javascript"),
        ):
            status, headers, body = get(self.base + url)
            self.assertEqual(status, 200)
            self.assertIn(kind, headers["Content-Type"])
            self.assertTrue(body)

    def test_path_traversal_and_database_download_are_denied(self):
        for path in (
            "/../contract.json", "/../../etc/passwd", "/%2e%2e/service.py",
            "/fixture.sqlite", "/contract.json", "/instructor/reference.py",
            "/.env",
        ):
            status, _, _ = get(self.base + path)
            self.assertEqual(status, 404, path)

    def test_browser_security_headers(self):
        status, headers, _ = get(self.base + "/")
        self.assertEqual(status, 200)
        self.assertIn("default-src 'none'", headers.get("Content-Security-Policy", ""))
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_no_cross_origin_read_permission_header(self):
        _, headers, _ = get(self.base + "/api/v1/events")
        self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_database_connection_cannot_write(self):
        conn = self.service._connect()
        try:
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM curated_events")
            self.assertEqual(conn.execute("SELECT count(*) FROM curated_events").fetchone()[0], 4)
        finally:
            conn.close()

    def test_missing_database_returns_503_without_path_disclosure(self):
        missing = Path(self.temp.name) / "does-not-exist.sqlite"
        other = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(missing))
        worker = Thread(target=other.serve_forever, daemon=True)
        worker.start()
        try:
            status, _, body = get("http://127.0.0.1:" +
                                  str(other.server_port) + "/api/v1/overview")
            self.assertEqual(status, 503)
            self.assertNotIn(str(missing).encode("utf8"), body)
            self.assertIn(b"unavailable", body)
        finally:
            other.shutdown()
            other.server_close()
            worker.join(timeout=5)

    def test_demo_bootstrap_never_overwrites_existing_database(self):
        with self.assertRaises(FileExistsError):
            create_demo_database(self.database)
        self.assertEqual(self.service.overview()["total_events"], 4)

    def test_empty_curated_table_is_reported_as_empty(self):
        with TemporaryDirectory() as folder:
            dbpath = Path(folder) / "empty.sqlite"
            with closing(sqlite3.connect(dbpath)) as db, db:
                load_stage07().ensure_schema(db)
            result = AnalyticsService(dbpath, clock=lambda: FIXED_NOW).overview()
            self.assertEqual(result["freshness_status"], "empty")
            self.assertIsNone(result["average_magnitude"])
            self.assertEqual(result["last_quality_status"], "unknown")

    def test_frontend_avoids_html_injection_sinks(self):
        js = (LAB / "web/app.js").read_text(encoding="utf8")
        self.assertIn(".textContent", js)
        self.assertIn("replaceChildren", js)
        self.assertNotIn(".innerHTML", js)
        self.assertNotIn("eval(", js)
        self.assertNotIn("http://", js)
        self.assertNotIn("https://", js)

    def test_frontend_distinguishes_quality_and_staleness(self):
        js = (LAB / "web/app.js").read_text(encoding="utf8")
        for required in (
            "freshness_status", "last_quality_status", "blocked", "stale",
            "getJSON", "no-store", "system-status",
        ):
            self.assertIn(required, js)


if __name__ == "__main__":
    unittest.main(verbosity=2)

