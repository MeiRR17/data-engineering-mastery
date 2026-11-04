-- Local-only synthetic SQL detective exercise
CREATE TABLE quake_events (
  row_id INTEGER PRIMARY KEY,
  event_id TEXT NOT NULL,
  location TEXT NOT NULL,
  occurred_on TEXT NOT NULL,
  magnitude REAL,
  updated_at TEXT NOT NULL
);
INSERT INTO quake_events(event_id,location,occurred_on,magnitude,updated_at) VALUES
 ('e1','Island A','2026-01-01',3.5,'2026-01-02T00:00:00Z'),
 ('e2','Island B','2026-01-01',NULL,'2026-01-02T01:00:00Z'),
 ('e2','Island B','2026-01-01',4.2,'2026-01-02T02:00:00Z'),
 ('e3','Island A','2026-01-02',4.0,'2026-01-03T00:00:00Z');
