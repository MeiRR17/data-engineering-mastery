# Stage 08 — Read-only Data Serving API and Quality-aware Dashboard

[Stage 08 syllabus](../../curriculum/modules/08.md) · [Stage 07 quality](../07-quality/README.md) · [DataPulse](../../projects/datapulse/README.md) · [Notebook](../../notebooks/08_readonly_serving.ipynb)

## Goal

Stage 07 created a quality gate that can **reject an invalid batch** while preserving a safe audit trail. Stage 08 turns approved data into a **read-only data product** with precisely defined metrics and a dashboard that reports stale data and the status of the latest quality run.

This lab uses only **Python's standard library**, synthetic SQLite records and a server bound to **127.0.0.1**. It does not require Docker, Supabase, cloud keys or paid services. It is an educational demonstration, **not a production API** and must not be exposed to the public internet.

~~~mermaid
flowchart LR
  A[Stage 07 data contract] --> B{Quality gate}
  B -->|passed| C[(Curated SQLite)]
  B -->|blocked| Q[(Safe quality audit)]
  C --> D[Read-only SQLite connection]
  D --> E[Allowlisted GET API]
  Q --> E
  E --> F[English dashboard]
  F --> G[Freshness and quality warnings]
~~~

## Run the demonstration

From the repository root:

~~~bash
python3 labs/08-serving/grade.py
python3 labs/08-serving/serve.py
~~~

The first command runs **24 HTTP, API and security tests** against a loopback server. The second creates a temporary SQLite dataset, processes one valid batch followed by one blocked batch and launches the local dashboard.

Open **http://127.0.0.1:8765** in a browser. Click **Refresh metrics**, inspect the charts and filter events by ID or region. Press **Ctrl+C** to stop.

**Expected teaching behavior:** the historical fixture was observed on **January 3, 2026**, so the dashboard will normally display a **stale data warning** on today's date. This is deliberate: a dashboard must never pretend historical data is a live stream.

### Privacy boundary

Without `--database`, the app creates a synthetic, temporary SQLite file that is removed on normal exit. You may pass an existing Stage 07 teaching database using `--database /path/to/file.sqlite`; it is opened **read-only**. Do not point this unauthenticated training app at real personal, customer or other sensitive records.

## Public API contract

| Endpoint | Exposed fields | Bounds |
| --- | --- | --- |
| `GET /api/v1/health` | Local fixture database availability | No private data |
| `GET /api/v1/overview` | Event count, mean, denominator, freshness and quality | No raw payload or digest |
| `GET /api/v1/daily?limit=14` | Aggregates by UTC date | 1–50 groups |
| `GET /api/v1/events?limit=20&offset=0` | Allowlisted curated events | `limit` 1–50; `offset` 0–1000 |
| `GET /api/v1/quality?limit=5` | Quality-run counts, statuses and reason codes | No raw records or source hashes |

SQL and exposed fields are fixed in source code. There is **no endpoint accepting arbitrary SQL or table names**. POST, PUT, PATCH, DELETE and HEAD are rejected, and invalid pagination input returns a client error.

The browser uses plain JavaScript with `textContent` instead of `innerHTML`, alongside Content Security Policy and other HTTP safety headers. These checks **do not replace** a complete threat model or penetration test.

## Quality and freshness are different signals

An incoming batch with an unknown schema field may be **blocked entirely** by the quality gate. Previously approved data can remain visible, but the latest run must be clearly marked blocked.

Freshness compares the most recent **event timestamp** with a UTC-aware clock. Data can be historically correct but unsuitable for decisions requiring real-time updates. Empty and API-error states must show explicit messages instead of zero-looking or stale KPI values.

## Independent Regional KPI challenge — 11 graded tests

In addition to the ready-to-run API demo, the student must implement `region_summary` in [learner/starter.py](learner/starter.py); it begins as `NotImplementedError`.

Return **one row per region** with total event count, count of known magnitudes and a mean excluding NULL. Sort by descending event count then ascending region code. Accept only integer `limit` values in the range **1–20**. Never expose event IDs, hashes or raw payload, overwrite the source DB or silently create a missing database.

~~~bash
# Validate the grader's instructor reference
python3 labs/08-serving/learner/grade.py --reference

# Grade student code — intentionally fails before implementation
python3 labs/08-serving/learner/grade.py

# Or grade a separate personal solution file
python3 labs/08-serving/learner/grade.py --answers path/to/region_report.py
~~~

The 11 scenarios include invalid inputs, NULL handling, correct grouping/averages, bounded rows, output allowlisting and no source-file modifications.

After passing, optionally add a new `GET /api/v1/regions` route and write at least one positive and one negative **HTTP** test. This route is an extension task, not already implemented by the starter grader.

## Required learner tasks

1. Draw the trust boundary: SQLite read-only → fixed SQL → bounded JSON → browser. What does **not** cross it?
2. Explain `total_events` vs `known_magnitude_events` and why the latter is the denominator for the magnitude mean.
3. Change `FRESHNESS_HOURS` to one in your practice branch and predict the status against a fixed clock.
4. Implement a regional summary query with fixed SQL and a parameterized LIMIT.
5. Test that the new route cannot expose `source_sha256`, `quarantine_records` or raw upstream metadata.
6. Simulate a missing database or API error and prove the dashboard shows a failure, not misleading values.
7. Write an ADR covering service-role credentials, CORS, authentication, authorization, rate limiting, reverse proxy and TLS.

## No-AI exit questions

- When can `AVG(magnitude)` be mathematically correct but misleading to a stakeholder?
- How should the UI behave if ingestion failed while the last published data remains queryable?
- How do database SELECT permissions and row-level security differ?
- Why is an unrestricted SELECT endpoint unsafe even without write statements?
- How would you paginate a changing data set without duplicating or skipping records?

**Exit gate:** original learner code, 24 API tests, 11 learner KPI tests, one new positive/negative HTTP test, correct Empty/Error/Stale display, a safety ADR and a reviewed PR.

**Not verified:** production authentication, TLS, Supabase cloud access, browser E2E across systems, multi-tenant permissions, operational monitoring or a cloud deployment. Do not publish this local teaching server to the internet.
