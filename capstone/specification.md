# DataPulse Capstone — Formal Product and Engineering Specification

Version: `capstone-spec-1.0` · Scope: junior Data Engineering competency through reproducible project evidence.

## Business objective

Build an auditable ingestion-to-serving data pipeline for synthetic seismic-like events. Stakeholder wants accurate daily/region event counts and magnitudes, with clear warnings for stale or quality-blocked data. No real public-safety decisions are allowed based on this learning demo.

**Definition of success:** duplicate/out-of-order events do not corrupt records; malformed source schema cannot silently reach serving; a failure before transaction commit leaves no partial effects; the latest accepted data can be queried safely; an independent backup restore recreates data; promotion and rollback are documented; evidence is reproducible.

## Input contract

- Required fields: `event_id`, `observed_at`, `source_updated_at`, `region_code`, `magnitude`.
- Source is `labs/11-streaming/data/synthetic_log.jsonl`: topic-partition-offset envelopes and synthetic JSON values.
- UTC-aware timestamps only. Region is an uppercase code. Event ID is a natural key. A new source revision may update old data by `source_updated_at`; ties require a stated deterministic policy.
- Unknown fields and malformed timestamps are quarantined without exposing the original payload.

## Data architecture and grains

| Asset | Grain | Key/invariant |
|---|---|---|
| Input topic log | message at topic/partition/offset | no conflicting duplicate envelope |
| Stream SQLite sink | latest business event | event_id |
| Offset checkpoints | consumer group/topic/partition | next committed offset; same transaction as sink |
| Quality run | source batch/run | run_id, status, allowed/blocked |
| Curated event | validated source event | event_id, source_updated_at, digest |
| Analytics API | query of curated events or daily groups | explicit field allowlist |
| Backup | complete SQLite database image | verified sha256 and integrity check |
| Release | versioned artifact | deterministic ZIP + trusted manifest scope |

## Functional acceptance requirements

| ID | Requirement | Validation |
|---|---|---|
| FR-01 | Event redelivery is safe | Stage 11 replay test |
| FR-02 | Poison event is quarantined with no raw payload | Stage 11 and Stage 07 |
| FR-03 | Batch below quality threshold publishes 0 events | Stage 07 and capstone blocked test |
| FR-04 | Recovered batch is idempotent | Stage 07 and capstone replay |
| FR-05 | Serving reports correct count and non-NULL average | Stage 08 and capstone |
| FR-06 | Backup restores into new isolated file | Capstone backup comparison |
| FR-07 | Release promotion rejects damaged/unhealthy artifacts | Stage 09 |
| FR-08 | Staging rollback leaves dev unchanged | Stage 09 and capstone |
| FR-09 | Evidence report records only safe facts | Capstone grader |
| FR-10 | Learner demonstrates an unseen changed source contract | Reviewer-only transfer exam |

## Nonfunctional acceptance targets

- **Correctness:** all instructor tests pass, student's own tests pass, no known integrity violations.
- **Security:** no cloud credentials, raw payload or secret in public API/logs; read-only access and denied write routes tested; cloud auth/RLS is a separate approval-gated task.
- **Performance:** small fixture only; do not extrapolate to production event rates. Record time/memory assumptions in learner benchmark.
- **Availability:** classroom exercise only. SLO target must be defined by stakeholder before measuring.
- **Observability:** freshness, quality and error budget simulated; real alerts require external environment tests.
- **Recovery:** integrity and row reconciliation of a restored SQLite copy. True RPO/RTO requires a production-like time-bound drill.
- **Reproducibility:** fixed synthetic fixture, deterministic reference checks, version-pinned optional tools and documented commands.

## Learner architecture decisions to record

1. ADR-001: Why the chosen source ingestion is batch, polling or Kafka under given latency/throughput and operational constraints.
2. ADR-002: Why the storage/warehouse uses Postgres/Supabase or alternatives, and how star-schema grain, SCD2 and RLS are enforced.
3. ADR-003: Why the serving layer is read-only, how freshness and errors are presented, and how auth/authorization would work in production.
4. Optional ADR-004: Scale choice (Spark vs local SQL) and evidence required to justify it.

## Release and reviewer governance

The student must not mark their system “deployed to cloud” without a successful authenticated endpoint smoke test and secret-protection evidence. The examiner must not issue a professional certificate by reading a passing instructor CI run. See [final assessment](../docs/FINAL-ASSESSMENT.he.md) for an external-review protocol and the exact score thresholds.

## Known exclusions

This learning reference has no real multi-node Kafka/Spark cluster, real-time alerting, managed production secrets, remote high-availability deployment, user-identifying datasets or measured cloud RPO/RTO. Additional hands-on full-mode environments can be added only after a separate security and resource review.
