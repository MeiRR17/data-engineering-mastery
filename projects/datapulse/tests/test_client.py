import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from datapulse.client import SupabaseRestClient
from datapulse.ingest import run


class FakeResponse:
    def __init__(self, obj):
        self.payload = json.dumps(obj).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return self.payload


class ClientTests(unittest.TestCase):
    def test_rpc_uses_secret_only_in_request_header(self):
        client = SupabaseRestClient("https://project.supabase.co/", "sb_secret_example")
        with patch("urllib.request.urlopen", return_value=FakeResponse(1)) as call:
            count = client.upload_batch([{"event_id": "demo"}])
            self.assertEqual(count, 1)
            request = call.call_args[0][0]
            self.assertEqual(request.full_url, "https://project.supabase.co/rest/v1/rpc/ingest_earthquake_batch")
            self.assertEqual(request.get_header("Apikey"), "sb_secret_example")
            self.assertIsNone(request.get_header("Authorization"))

    def test_no_remote_write_for_dry_run(self):
        source = json.loads((ROOT / "data" / "sample.geojson").read_text())
        with patch("urllib.request.urlopen") as call:
            output = run(source, client=None)
            self.assertEqual(output["loaded_rows"], 0)
            call.assert_not_called()

    def test_invalid_origin_rejected(self):
        with self.assertRaises(ValueError):
            SupabaseRestClient("http://public-host.example", "secret")


if __name__ == "__main__":
    unittest.main()
