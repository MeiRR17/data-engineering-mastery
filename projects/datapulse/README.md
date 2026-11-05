# DataPulse — From a Data API to Trusted Analytics

[Course home](../../README.md) · [DataPulse learning path](LEARNING-PATH.he.md) · [Deployment checklist](DEPLOYMENT-CHECKLIST.he.md)

**Project architecture:** USGS GeoJSON → Python ETL → PostgreSQL/Supabase → read-only dashboard → optional deployment. It is a learning project with **synthetic offline fixtures** and optional, owner-authorized live integration. Neither a deployed cloud project nor production readiness is implied by the code.

## What problems does it solve?

- **Extract:** request a USGS earthquake GeoJSON feed; official source: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php.
- **Transform:** validate event ID, timestamps, coordinates, magnitude, event type and quality of records.
- **Load:** persist raw and curated records in a PostgreSQL transaction; upsert by business `event_id` and source revision time.
- **Quality:** quarantine malformed input, enforce a demonstrative 25% rejection threshold and database constraints, test failure cases.
- **Serve:** return approved curated data through a restricted read-only PostgREST view, governed by RLS and minimal grants.
- **Operate:** explicitly enabled scheduled ingestion, run logs and safe dry-run behavior.
- **Deploy:** optionally use a *separate* Supabase database sandbox and Vercel for the static frontend, only with owner permission and a cost review.

~~~mermaid
flowchart TD
  A[USGS GeoJSON feed] --> B[Python ingestion]
  B --> C{Validate event contract}
  C -->|approved| D[Postgres ingestion function]
  C -->|rejected| E[Safe rejection counters]
  D --> F[(Private raw JSONB)]
  D --> G[(Curated event records)]
  G --> H[Daily SQL view]
  H --> I[Restricted REST read API]
  G --> I
  I --> J[Static dashboard]
  K[Optional approved schedule] --> B
~~~

### Important boundaries

1. Supabase/PostgreSQL is sufficient for this teaching scale; it is **not** a substitute for Spark or a dedicated distributed warehouse at all scales.
2. `SUPABASE_SECRET_KEY` / service-role credentials belong **server-side only**. Never embed them in JavaScript or commit them to Git.
3. A publishable key can be publicly exposed **only if** RLS, GRANT and API exposure rules are independently verified.
4. Raw input and ingestion audit tables are private. Anonymous clients should see only explicitly approved curated records/aggregates.
5. Re-ingesting an event cannot create another record for the same `event_id`. A newer source revision may update the record.
6. `data/sample.geojson` is synthetic. Never represent its records as actual real-world earthquakes.

## Where to run the commands

This project lives at `projects/datapulse/` in the course repository. In the commands below, first enter that folder **from the repository root**:

~~~bash
cd projects/datapulse
~~~

The directory structure is:

~~~text
src/datapulse/etl.py      deterministic transform and quality rules
src/datapulse/ingest.py   CLI entry point, HTTP fetch, retry and dry-run
src/datapulse/client.py   Supabase REST adapter
database/001_init.sql     PostgreSQL schema, view, RLS and ingest function
web/                      accessible English static dashboard and API configuration
data/sample.geojson       synthetic fixture
tests/                    unittest coverage
scripts/                  CLI-managed migration helper
~~~

The GitHub Actions ingestion workflow is maintained in the course repository's root-level `examples/workflows/ingest.yml.example`, not inside this project folder.

## Step 1 — run everything locally, with no cloud cost

**Requirement:** Python 3.11+.

~~~bash
# Start at the course root, then:
cd projects/datapulse
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m datapulse.ingest \
  --fixture data/sample.geojson --dry-run
~~~

A dry run should write **zero** database rows. A real request to the public feed is optional and needs internet access:

~~~bash
PYTHONPATH=src python3 -m datapulse.ingest --feed day --dry-run
~~~

Read output as a diagnostic. Never assume the feed or its schema is fixed forever.

## Step 2 — optional, separately approved Supabase project

Only proceed if the owner has explicitly authorized creating a **new isolated sandbox**, has checked potential billing, and has selected the correct Supabase account/organization.

1. Open https://supabase.com/dashboard and inspect account, region, billing and security settings.
2. Create a *new* project, not one holding personal or business data.
3. Choose **one** migration path: SQL Editor *or* versioned CLI migrations. Do not execute the initial migration twice.
4. Inspect [database/001_init.sql](database/001_init.sql) before using it.
5. Confirm `raw_earthquakes`, `earthquakes`, `ingest_runs` and `daily_stats`, including grants and exposed Data API schemas.
6. Keep secret keys in a secure backend/CI store; never share them with an AI tutor.

For the CLI method, check the exact current syntax **before** proceeding. Examples from a development environment:

~~~bash
supabase --version
supabase --help
supabase init
bash scripts/create_migration.sh
# Review the generated migration and get approval before linking or pushing.
# Only then, in the authorized sandbox:
supabase login
supabase link --project-ref YOUR_APPROVED_PROJECT_REF
supabase db push --remote
~~~

See the [controlled Supabase deployment guide](../../docs/STAGE-04-SUPABASE-DEPLOY.he.md). Do not copy cloud commands without reviewing their effect and your CLI version.

## Step 3 — first approved ingestion

In a protected terminal/session, supply **server-side** environment variables only:

~~~bash
export SUPABASE_URL=https://YOUR_APPROVED_PROJECT_REF.supabase.co
export SUPABASE_SECRET_KEY='YOUR_SERVER_SIDE_SECRET_KEY'
PYTHONPATH=src python3 -m datapulse.ingest --feed day
~~~

Check database state using approved SQL access:

~~~sql
select count(*) from public.raw_earthquakes;
select count(*) from public.earthquakes;
select * from public.daily_stats order by day desc limit 7;
select status, source_rows, valid_rows, rejected_rows, loaded_rows
from public.ingest_runs order by started_at desc limit 5;
~~~

### Idempotency check

Run the same batch again and compare IDs and counts. A replay must not insert duplicate IDs. If the upstream data actually changed between runs, new events or revised values are legitimate; assess source revision times before declaring a problem.

## Step 4 — visually inspect the English dashboard

A local demo requires **no account, key or cloud service**. Starting inside `projects/datapulse`:

~~~bash
cd web
python3 -m http.server 8080
# Open http://localhost:8080/?demo=1
~~~

For a separately authorized Supabase-backed local demo, create `web/config.local.js` from `web/config.local.example.js` and include **only** the public URL and publishable key. Do not include a secret token in `web/`.

For optional Vercel hosting, connect the intended GitHub repository and set the correct root directory `projects/datapulse/web` when importing the monorepo. Set only public configuration values needed by the frontend. Verify `/api/config` does not return privileged keys. Check status codes, loading/error/empty states, GRANT and RLS on the actual deployed API; **a screenshot is not an authorization test**.

## Step 5 — optional, explicit schedule

The sample workflow lives at [examples/workflows/ingest.yml.example](../../examples/workflows/ingest.yml.example). It is disabled by default and **must not be activated without approval**. To enable it:
- Review the workflow and copy it to the monorepo's `.github/workflows/` under an approved PR.
- Configure `SUPABASE_URL` and `SUPABASE_SECRET_KEY` as repository **secrets**, not public variables.
- Set `DATAPULSE_ENABLED=true` only after a successful manual dry run and cost review.
- Monitor schedule drift, retries, error logs, quotas, budget alerts and the shutdown procedure.

GitHub's scheduled Actions are not guaranteed to run at an exact minute.

## Step 6 — security and quality exit gate

- [ ] Raw and audit tables are **not readable** with anonymous/public credentials.
- [ ] Curated tables and approved metrics can be read, but **not written**, with public credentials.
- [ ] The ingest function is not callable by anonymous/authenticated frontend users.
- [ ] No server-side secret appears in browser bundles or Git history.
- [ ] HTTP errors and invalid records cannot silently bypass quality gates.
- [ ] Supabase security/performance advisors have no unresolved critical findings.
- [ ] Replays do not add duplicates, and later source corrections are applied correctly.
- [ ] The dashboard handles no data, network failure and NULL magnitudes.
- [ ] Operational limits and the cost estimate are documented.

## Limits and advanced learning

- A daily feed is usually a **rolling window**, not a complete historical archive. Historical analytics need a bounded, safe backfill.
- `loaded_rows` represents rows submitted to the ingestion function, not necessarily rows actually changed.
- Unit tests do not replace integration tests against real PostgreSQL.
- The average magnitude excludes NULL from the denominator; make that denominator explicit.
- The frontend is a static web app; PostgreSQL/Supabase is the backend, not a frontend hosting provider.
- The course includes separate **dbt**, **PySpark**, **Kafka** and **CI/CD** labs; those are not automatically deployed by this DataPulse MVP.

## Official references

- [USGS feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)
- [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys)
- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase deployment](https://supabase.com/docs/guides/deployment)
- [Vercel Functions](https://vercel.com/docs/functions)

**Do not claim remote Supabase deployment or production readiness without owner-approved remote security, data API and restore evidence.**
