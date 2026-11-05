# DataPulse — safe deployment checklist, not an automatic push recipe

The course uses **synthetic data**. Cloud deployment is optional, billable and permitted only in an owner-approved sandbox. Passing local tests does not imply cloud deployment or production readiness.

## Phase 1 — local and offline

~~~bash
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
PYTHONPATH=projects/datapulse/src python3 -m datapulse.ingest \
  --fixture projects/datapulse/data/sample.geojson --dry-run
~~~

A correct dry run should **not write to a database** (`loaded_rows: 0`). Verify the input is synthetic before proceeding.

## Phase 2 — separate cloud account and project

1. Choose a learner-owned Supabase organization, cost limit and region. Never use someone else's existing database for an exercise.
2. Store credentials in an approved secret manager or protected environment, not a frontend file.
3. Check the current `supabase --version` and `supabase db --help`. Confirm how your CLI distinguishes local and remote operations.
4. In `projects/datapulse`, initialize an isolated Supabase project if needed and use [the migration creation helper](scripts/create_migration.sh).
5. Test `supabase start` and any local reset **only in disposable local development**. Never perform a reset against valuable remote data.
6. Request explicit approval before running a remote migration; review the SQL/permissions and supported CLI syntax first.

## Phase 3 — security before public exposure

- [ ] Row-level security is enabled on raw and curated database tables where required.
- [ ] Anonymous roles cannot INSERT, UPDATE or DELETE internal records.
- [ ] Anonymous access is limited to explicitly approved dashboard data/views.
- [ ] Privileged ingest functions cannot execute with public credentials.
- [ ] A serving view has appropriate security-invoker semantics and restricted grants.
- [ ] Secret/service-role credentials remain server-side; publishable keys are used only with proven authorization.
- [ ] Database security/performance advisors have been reviewed and findings resolved or documented.

## Phase 4 — ingestion and idempotency

- Store `SUPABASE_URL` and `SUPABASE_SECRET_KEY` only in protected server-side configuration.
- Load a **small synthetic** source; compare database counts and provenance.
- Repeat the batch: there should be no new row for the same business event ID.
- Inject a timeout, invalid payload, HTTP 429 and bad credential in a safe environment; do not report false success.
- Compare checksum/quality metrics and document rejected rows.

## Phase 5 — dashboard

For a purely local demo, serve `projects/datapulse/web` from localhost and open its `?demo=1` mode. If separately approved for static deployment, configure the frontend build's root directory and **public-only** environment values at the hosting provider.

Verify actual HTTP responses and **loading/error/empty** states; screenshots do not prove authorization.

## Phase 6 — optional scheduled ingestion

The sample workflow is [examples/workflows/ingest.yml.example](../../examples/workflows/ingest.yml.example). Do not activate it automatically. After the owner approves deployment:
1. Review its commands/`PYTHONPATH` and scope them to the repo.
2. Configure GitHub repository secrets only through authorized settings.
3. Set `DATAPULSE_ENABLED=true` only after a successful dry run and budget review.
4. Inspect logs, quotas, failure alerts, replay and a documented shutdown plan.

## Evidence required after an approved remote deployment

- A live URL **and actual endpoint smoke tests**, not only a screenshot.
- PR/commit SHA, CI result, SQL queries and negative RLS tests.
- Runbook for logs, backfill, restore and disabling schedulers.
- Cost assumptions, API limits and ingestion frequency.

**This checklist does not perform a deployment.** Do not claim a production capability without real remote security, monitoring and restore verification.
