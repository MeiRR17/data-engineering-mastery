# Stage 13 — DataPulse End-to-End Capstone

[Formal specification](specification.md) · [Stage 13 course](../curriculum/modules/13.md) · [Independent assessment](../docs/FINAL-ASSESSMENT.he.md)

The final project is a **single product**, not 14 isolated demo snippets. You demonstrate how a source event becomes an auditable, trustworthy, queryable and recoverable data product, and you must defend its architecture, performance, security and operations.

## Architecture

~~~mermaid
flowchart LR
  A[Streaming synthetic JSONL / Stage 11] --> B[Transactional offsets + sink]
  B --> C[Stage 07 versioned contract and quality gate]
  C -->|bad batch| Q[Quarantine + blocked audit]
  C -->|valid| D[(Curated SQLite)]
  D --> E[Stage 08 read-only analytics API]
  D --> F[Verified backup + restore to new file]
  E --> G[Versioned Stage 09 release artifact]
  F --> R[Disaster recovery verification]
  G --> H[Simulated staging promotion and rollback]
  Q --> I[Data quality incident evidence]
  H --> J[Capstone evidence report]
  R --> J
  I --> J
~~~

## Prerequisites

Complete practical Stages 00–12 and their assigned conceptual gates. The project is intentionally lightweight enough for a normal personal computer: **Python 3.11+**, SQLite in the standard library, no Docker, no third-party package, no cloud account and no private data. Successful execution of the instructor reference is a preflight for your own implementation, not proof of your skills.

## Run from repository root

~~~bash
# Check the integrated reference against 22 automated, multi-stage tests:
python3 capstone/grade.py --reference

# Simulate a full pipeline, with temporary files cleaned up after execution:
python3 capstone/demo.py

# Keep the synthetic artifacts under a NEW directory if you want to inspect:
python3 capstone/demo.py --workspace /tmp/dem-stage13-first-run

# Implement your capstone and test it (expected to fail initially):
python3 capstone/grade.py
~~~

The `--workspace` argument must point to a **new, nonexistent** directory. Do not use a directory containing real datasets, saved work or credentials.

The reference pipeline produces exactly four accepted event IDs and two dead-letter records. A deliberately malformed batch is rejected without publishing changes. An idempotent recovery pass is accepted without duplicating rows. The read-only API correctly reports event count, non-NULL magnitude denominator and data freshness. SQLite backup integrity and restore are verified before a synthetic release is promoted and rolled back.

## Learner deliverables

1. **Your own orchestration:** implement `capstone/starter.py::run_pipeline` by composing the earlier modules, not copying the instructor implementation. Pass all 22 integration tests.
2. **Reliable data model:** show the source/business key, raw/curated separation, UTC event time, schema contract, quality thresholds, SCD2/Star Schema decisions and unique fact grain.
3. **Two operational failures:** intentionally introduce a stream crash before transaction commit and a quality-blocked batch. Demonstrate recovery, replay and correct downstream metrics.
4. **Security and privacy:** API is read-only, raw payload remains private, denied operations are tested, invalid events are quarantined using safe reason codes.
5. **Shipping and recovery:** build an immutable versioned artifact with SHA; demonstrate staging promotion failure and rollback. Restore into a new file and compare results to known-good data.
6. **Production architecture plan:** create ADRs for orchestration, storage and serving; compare Kafka vs batch, PySpark vs PostgreSQL and Supabase vs self-hosted Postgres based on realistic workload assumptions.
7. **SLO/cost:** define freshness and availability metrics, error budget, a cost scenario and escalation criteria, and show how you would instrument and alert.
8. **Reproducibility:** one-page README with exact commands, source data lineage, test evidence, design decisions and limitations.
9. **Demo:** present the pipeline in 10 minutes, show a broken case and restoration, and explain tradeoffs without AI.
10. **Unseen transfer:** receive a different synthetic dataset/contract and adapt the solution without opening the instructor reference.

## Required 10-minute demo

| Time | Demonstration |
|---|---|
| 0:00–1:00 | Business problem, input contract, architecture, data flow |
| 1:00–3:00 | Event ingestion, checkpoint and idempotency evidence |
| 3:00–4:30 | Quarantine a malformed event, show no accidental publication |
| 4:30–6:00 | Read-only serving, correct metrics, stale/blocked-state handling |
| 6:00–7:30 | Restore a verified backup and compare source/restore |
| 7:30–8:30 | Release artifact verification and simulated rollback |
| 8:30–10:00 | Scale, security, costs, alternative tools, important limits |

## Exit criteria and portfolio claims

- [ ] All 22 automated capstone cases pass on your own implementation.
- [ ] The reviewer witnesses the demo, tests one unseen variation and reviews source code originality.
- [ ] At least 3 ADRs with alternatives, tradeoffs and rejected options.
- [ ] Passes the independent final exam in [FINAL-ASSESSMENT.he.md](../docs/FINAL-ASSESSMENT.he.md).
- [ ] No secret exposure, privacy violation or unresolved critical security issue.
- [ ] Published portfolio case study distinguishes **local simulation**, **real integration**, and **cloud deployment** with evidence for each.
- [ ] Completed evaluation reviewed and signed by an identified qualified reviewer.

This capstone's reference pipeline is **local and synthetic**, not a production platform. It does not establish enterprise Kafka exactly-once, remote Spark performance, cloud authentication/RLS, real disaster-recovery RPO/RTO or an externally accredited professional credential. An internal completion certificate can be considered only after independent human assessment.
