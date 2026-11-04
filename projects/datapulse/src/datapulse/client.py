"""Minimal Supabase REST client using the current secret-key header convention."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class SupabaseRequestError(RuntimeError):
    pass


class SupabaseRestClient:
    def __init__(self, url: str, secret_key: str):
        if not url.startswith("https://") and not url.startswith("http://127.0.0.1:"):
            raise ValueError("SUPABASE_URL must use HTTPS (localhost exempted)")
        if not secret_key:
            raise ValueError("missing SUPABASE_SECRET_KEY")
        self.base = url.rstrip("/") + "/rest/v1/"
        self.key = secret_key

    def request(self, method: str, resource: str, payload: Any = None, extra_headers: dict[str, str] | None = None) -> Any:
        if resource.startswith(("/", ".")) or ".." in resource or not (resource.startswith("rpc/") or resource.startswith("ingest_runs")):
            raise ValueError("resource must be a single REST route")
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"apikey": self.key, "Content-Type": "application/json", "Accept": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(self.base + resource, data=body, headers=headers, method=method)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = response.read()
                    return json.loads(data) if data else None
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    message = exc.read(400).decode("utf-8", "replace")
                    raise SupabaseRequestError(f"Supabase HTTP {exc.code}: {message}") from exc
                retry_after = exc.headers.get("Retry-After", "")
                wait = min(int(retry_after), 15) if retry_after.isdigit() else 2 ** attempt
                time.sleep(wait)
            except urllib.error.URLError as exc:
                if attempt == 2:
                    raise SupabaseRequestError(f"Supabase network error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
        raise AssertionError("unreachable")

    def start_run(self, run_id: str, feed_name: str) -> None:
        self.request("POST", "ingest_runs", {"run_id": run_id, "feed_name": feed_name, "status": "running"}, {"Prefer": "return=minimal"})

    def finish_run(self, run_id: str, **changes: Any) -> None:
        query = "ingest_runs?run_id=eq." + urllib.parse.quote(run_id, safe="")
        self.request("PATCH", query, changes, {"Prefer": "return=minimal"})

    def upload_batch(self, rows: list[dict[str, Any]]) -> int:
        result = self.request("POST", "rpc/ingest_earthquake_batch", {"p_rows": rows})
        return int(result)
