# Stage 04 — PostgreSQL / Supabase real-database lab

[Stage 04](../../curriculum/modules/04.md) · [Cloud guide](../../docs/STAGE-04-SUPABASE-DEPLOY.he.md)

## Goal
Build an evidence-backed PostgreSQL data pipeline with row-level security, least-privilege SQL grants, a security-invoker view, atomic updates and repeatable ingestion. The local version **does not access or create any Supabase cloud project**.

The runner creates one **disposable PostgreSQL Docker container** with no published ports and no mounted volumes. It removes only the container it created. The fixture is entirely synthetic.

## Run from repository root
1. Install and start Docker Desktop/Engine. Do not proceed without reviewing run_lab.py.
2. Check: docker --version
3. Baseline (instructor reference): python3 labs/04-postgres/run_lab.py --reference
4. Student exercise: python3 labs/04-postgres/run_lab.py
5. Edit labs/04-postgres/starter.sql until your run passes. The default exercise **must initially fail** because it is incomplete.
6. Optionally submit a separate answer file: python3 labs/04-postgres/run_lab.py --answers path/to/my.sql

## Your assignment
Create a view named public.stage04_magnitude_summary with columns band (text) and total_events (bigint). Group magnitudes into unknown (NULL), minor (<2), moderate (2 to <5), strong (>=5). Make the view security_invoker=true and grant anon SELECT only after revoking default access. The tests assert positive access and negative attempts.

## Why this matters
* GRANT answers which operations a role can perform; RLS governs which rows can be accessed during a permitted operation.
* A PostgreSQL view defaults to owner-level checks, which can accidentally bypass the caller's RLS permissions.
* A retry must be idempotent. A multi-row write must be atomic if one row violates constraints.
* A stale source update must not replace fresher information.

## Exit gate
Explain these concepts without AI, run tests, show a PR with sanitized evidence and predict what happens if a process crashes after the database commits but before receiving an acknowledgement. Then independently design two tests for an additional read-only analytics view.

Passing this lab proves **local PostgreSQL integration**, not Supabase Auth, remote Data API exposure or cloud deployment. Those require the independent acceptance tests in the cloud guide.
