# Teaching plan — Data Engineering Mastery

[All 14 stages](ROADMAP.md) · [Mastery matrix](MASTERY-MATRIX.md) · [Project ladder](PROJECT-LADDER.md) · [Capstone](../capstone/README.md) · [Final assessment](FINAL-ASSESSMENT.md)

The pathway is suitable for a software engineering graduate but **does not assume** practical mastery of advanced SQL, database administration, networking, DevOps, streaming or production incidents. The learning cycle is:

**Explain → Predict → Experiment → Inject failure → Repair → Apply to an unseen case.**

## Suggested weekly pattern

Begin with a diagnostic. For a 10–12-hour week, a useful starting distribution is **2–3 hours theory**, **5–6 hours coding/labs**, **1–2 hours testing and incident debugging**, and **1 hour review/independent explanation**. Allocate roughly 70% to Data Engineering, 20% to CS bridges and 10% to revision/transfer.

These are flexible recommendations. **Progress is decided by demonstrated exit criteria, not weeks elapsed.**

| Phase | Stages | Core focus | Required artifact |
| --- | --- | --- | --- |
| A — Foundations | 00–03 | Git/OS, SQL, Python and idempotent ETL | Tested source-to-curated pipeline |
| B — Data product core | 04–05 | PostgreSQL, security, warehouse and dbt | Fact/dimension model with SCD2 and RLS tests |
| C — Reliable delivery | 06–09 | DAGs, quality, API serving and CI/CD | Reproducible, recoverable data product |
| D — Scale and streaming | 10–11 | Spark, shuffle/skew, Kafka and offsets | Matching Light/Full results and safe replay |
| E — Operations | 12 | SLOs, backup/restore, cost, RBAC and incidents | Evidence-backed incident report |
| F — Independent portfolio | 13 | Capstone, ADRs, interview and unseen exam | Original PR, demo and reviewer assessment |

## Standard lesson flow

1. **Define:** identify the consumer, source grain and failure scenario.
2. **Predict:** the learner forecasts the result or error code before execution.
3. **Investigate:** use an official reference, a visual notebook and a CS bridge.
4. **Implement:** complete `starter.py` or `starter.sql` on a personal branch.
5. **Break:** inject NULL, duplicate, bad timestamp, crash, replay or permission denial.
6. **Repair:** add a focused regression test and justify the fix.
7. **Defend:** explain alternatives, costs and constraints without AI.
8. **Record:** preserve PR/commit, exact commands, redacted logs, ADR and reviewer notes.

## Practice that cannot be skipped

- **SQL:** JOIN cardinality, window functions, `EXPLAIN` and unique fact grain.
- **Python:** parser handling wrong types, UTC timestamps, NULL and schema drift.
- **ETL:** at-least-once input, idempotent sink and atomic transactions.
- **PostgreSQL:** actual migrations and negative GRANT/RLS tests.
- **Warehouse/dbt:** SCD2, daily UTC mart, lineage and reconciled metrics.
- **Orchestration:** DAG ordering, bounded retries/backfill and checkpoints.
- **Quality:** versioned contract, completeness, freshness and safe quarantine.
- **Serving:** GET allowlist, correct average denominator and stale/error states.
- **Delivery:** deterministic build, integrity verification and rollback.
- **Spark:** local JVM, repartition, shuffles, Window and skew measurements.
- **Kafka:** real broker full-mode test, offsets, replay and lost acknowledgement.
- **Operations:** restore-to-new, threat model, SLO alert and cost assumptions.
- **Capstone:** end-to-end demo, three ADRs, an incident and independent exam.

## Hardware and cloud choices

**Light:** Python 3.11+ with SQLite and guided notebooks; good for everyone. **Moderate:** Docker/PostgreSQL/dbt. **Full:** Java, PySpark and single-node Kafka with available memory. No GPU required.

If a full-mode runtime is unavailable, mark its practical evidence **deferred**, not passed. Any cloud environment requires owner approval, resource limits, credentials protection and billing review.

## Who qualifies for internal completion review?

A learner must independently complete all 14 stage gates, provide original code/evidence, pass an unseen final exam, demonstrate failure recovery and have the capstone reviewed by a qualified person. An internal completion statement is **not an externally accredited certification**. CI checks code examples, not identity, originality or professional experience.
