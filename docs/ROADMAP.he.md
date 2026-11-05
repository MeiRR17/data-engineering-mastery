# Learning roadmap — from foundations to a Data Engineering capstone

This program is **competency-based**, not a fixed-hours checklist. It primarily targets software engineering graduates, but missing prerequisites can be learned using the Computer Science bridges and foundation labs.

## The 14 stages

| Stage | Subject | Track | Practical result |
| --- | --- | --- | --- |
| [00](../curriculum/modules/00.md) | Setup, Git and engineering diagnostics | Foundation | Reproducible environment and data-flow sketch |
| [01](../curriculum/modules/01.md) | SQL and relational correctness | Foundation | JOINs, windows, transactions and EXPLAIN |
| [02](../curriculum/modules/02.md) | Python for data | Foundation | Type-safe parser and regression tests |
| [03](../curriculum/modules/03.md) | Incremental batch ETL | Core | Replay-safe synthetic SQLite ingest |
| [04](../curriculum/modules/04.md) | PostgreSQL security; optional Supabase sandbox | Core | Migrations, grants, RLS negative tests |
| [05](../curriculum/modules/05.md) | Warehouse modeling and dbt | Core | Star schema, SCD2 and reconciled data marts |
| [06](../curriculum/modules/06.md) | Orchestration | Core | DAG, retries and bounded backfill |
| [07](../curriculum/modules/07.md) | Data quality and lineage | Core | Contract gate, safe quarantine and audit |
| [08](../curriculum/modules/08.md) | Analytics serving | Core | Read-only API and quality-aware dashboard |
| [09](../curriculum/modules/09.md) | Release engineering / CI/CD | Advanced | Reproducible artifact, health gate and rollback |
| [10](../curriculum/modules/10.md) | Big Data and Spark | Advanced | Real local PySpark, shuffle and skew analysis |
| [11](../curriculum/modules/11.md) | Kafka and streaming | Advanced | Consumer offsets, duplicates, replay and broker demo |
| [12](../curriculum/modules/12.md) | Reliability and governance | Advanced | SLO, risk register, incident, backup and restore |
| [13](../curriculum/modules/13.md) | Capstone and portfolio | Portfolio | End-to-end demo, ADRs, PR review and assessment |

[Foundation labs](FOUNDATIONS-LABS.he.md) provide executable SQL/Python/ETL graders. Every other stage also includes a practical lab and an original student implementation. **Passing a reference grader proves only that the exercise is runnable.**

## Three layers in each stage

1. **Engineering:** Build and test a measurable, reproducible data component.
2. **Computer Science:** Explain why it works using one [bridge](COMPUTER-SCIENCE-BRIDGES.he.md), not only a copied command.
3. **Optional side quest:** A small related challenge from [side-quests.json](../curriculum/side-quests.json).

The parallel [Foundations Passport](BREADTH-FOUNDATIONS.he.md) contains 12 cross-discipline quests spanning the 14 stages. They build problem-solving confidence without becoming a second degree.

## Flexible time expectations

| Weekly practice | Rough planning horizon | Important qualification |
| --- | --- | --- |
| 5–7 hours | Often 15–24+ months | Strongly affected by prior skills and runtime availability |
| 10–15 hours | Roughly 9–15+ months | Includes an initial capstone, not automatic certification |
| 20+ hours | Can progress faster | Only after independent transfer and code reviews pass |

These are **planning estimates, not guarantees**. A learner with established knowledge may move faster; someone encountering SQL or operating systems for the first time may need additional time. The [teaching plan](TEACHING-PLAN.he.md) gives a session structure.

## After the capstone: optional specializations

- **Data platforms:** Iceberg/Delta, schema registries, governance and platform self-service.
- **Analytics Engineering:** dbt, semantic metrics, SCDs and warehouse tuning.
- **Streaming:** Flink, event-time windows, state and exactly-once caveats.
- **AI data infrastructure:** RAG ingestion, chunk quality, embeddings, evaluation and privacy.
- **Architecture and reliability:** multi-region systems, incident reviews, SLOs and costs.

Choose one direction and create a new benchmarked, tested, security-reviewed capstone. The base program does not confer seniority or replace professional team experience.
