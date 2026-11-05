# Project Ladder — improve one DataPulse product across all 14 stages

[Home](../README.md) · [DataPulse](../projects/datapulse/README.md) · [Capstone](../capstone/README.md)

You do **not** abandon a project after every lesson. The synthetic DataPulse event-to-analytics product grows as you learn. You can later choose another safe domain (transit, weather or licensed open data), provided the schema, quality and reproducibility principles remain explicit.

| Stage | Product increment | Deliverable | Fault the tests should catch |
| --- | --- | --- | --- |
| 00 | Project zero | Python/Git, environment, notebook | Missing dependency / unsupported Python |
| 01 | SQL lab | Event table and queries | Duplicate business key or multiplicative JOIN |
| 02 | Parser | Strict type validation and UTC | Missing field or naive timestamp |
| 03 | Local ETL | Replay-safe SQLite loading | Two identical runs increase event count |
| 04 | PostgreSQL | Migrations, private raw schema, negative RLS tests | Anonymous write/read becomes possible |
| 05 | Analytics mart | Facts/dimensions, SCD2 and daily metrics | Wrong grain or historical JOIN fan-out |
| 06 | Scheduler | DAG, retries and bounded backfill | Failed task is silently marked completed |
| 07 | Quality gate | Versioned contract and quarantine | Malformed batch reaches curated data |
| 08 | Serving | Read-only API and freshness-aware dashboard | Unauthorized write or stale UI |
| 09 | Release | CI, signed/provenance-aware design and rollback simulation | Damaged or unhealthy release promoted |
| 10 | Big data | Local PySpark, skew and correctness | Wrong aggregation after partition shuffle |
| 11 | Streaming | Local Kafka producer/consumer and offset logic | Replay or out-of-order correction corrupts state |
| 12 | Operations | SLO, incident, backup/restore exercise | Missing freshness alert or corrupt restore |
| 13 | Portfolio | Integrated DataPulse demo and ADRs | A new engineer cannot reproduce the project |

For every stage, complete the **core coding task**, a relevant **CS bridge**, and optionally one 10–25 minute **side quest**. A side quest becomes mandatory only if a diagnostic reveals a serious prerequisite gap.

## Portfolio milestones

After Stage 03 you can accurately show a **local ETL demo**. Stages 04–09 teach warehouse, security, serving and delivery patterns; **only a verified real deployment** can substantiate a cloud-hosted claim. Stages 10–12 add scaling, streaming and operations concepts and corresponding local runtime evidence. Stage 13 combines them into a defensible case study.

A complete capstone is not an automatic substitute for team experience or senior-level production ownership.
