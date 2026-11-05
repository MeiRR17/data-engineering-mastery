-- Synthetic data: not scraped from private systems.
set role service_role;
select public.ingest_earthquake_batch($fixture$
[
 {"event_id":"lab-a","observed_at":"2026-01-01T10:00:00Z","source_updated_at":"2026-01-01T10:10:00Z","magnitude":1.5,"place":"Synthetic North","longitude":35.1,"latitude":31.2,"depth_km":5,"source_url":"https://example.org/lab-a","payload_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","raw_payload":{"source":"synthetic","id":"lab-a"}},
 {"event_id":"lab-b","observed_at":"2026-01-01T11:00:00Z","source_updated_at":"2026-01-01T11:10:00Z","magnitude":4.1,"place":"Synthetic East","longitude":35.3,"latitude":30.9,"depth_km":11,"source_url":"https://example.org/lab-b","payload_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","raw_payload":{"source":"synthetic","id":"lab-b"}},
 {"event_id":"lab-c","observed_at":"2026-01-02T08:00:00Z","source_updated_at":"2026-01-02T08:10:00Z","magnitude":5.7,"place":"Synthetic South","longitude":35.0,"latitude":30.1,"depth_km":8,"source_url":"https://example.org/lab-c","payload_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","raw_payload":{"source":"synthetic","id":"lab-c"}},
 {"event_id":"lab-d","observed_at":"2026-01-02T09:00:00Z","source_updated_at":"2026-01-02T09:10:00Z","magnitude":null,"place":"Synthetic West","longitude":34.9,"latitude":31.4,"depth_km":9,"source_url":"https://example.org/lab-d","payload_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","raw_payload":{"source":"synthetic","id":"lab-d"}}
]
$fixture$::jsonb);
reset role;
