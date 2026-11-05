# Mastery Matrix — how to measure Data Engineering competence

[Home](../README.md) · [Grading rubric](ASSESSMENT.md) · [Final assessment](FINAL-ASSESSMENT.he.md)

Rate **evidence, not confidence**. Use 0 = unfamiliar, 1 = can explain, 2 = can implement with guidance, 3 = can independently implement and debug, 4 = can defend trade-offs and transfer to an unseen problem. A score of 4 in this program is **not** a senior job title.

## Core skill checks

| Area | Evidence for level 3–4 | Stage |
| --- | --- | --- |
| SQL joins, windows, NULL | Explain cardinality and write new queries independently | 01 |
| Transactions and indexes | EXPLAIN analysis, ACID, locks and isolation | 01/04 |
| Python typing and testing | Input parser robust to new malformed cases | 02 |
| APIs, rate limiting | Bounded retries, timeouts and pagination | 02–03 |
| Incremental ETL | Upserts, checkpoints, replay and late corrections | 03–04 |
| Warehouse modeling | Fact grain, dimensions, SCD2 and costs | 05 |
| Batch orchestration | DAG, retries, restart and bounded backfill | 06 |
| Data quality/lineage | Completeness, uniqueness, freshness and provenance | 07 |
| Serving/privacy | KPI correctness, safe cache/permissions and negative tests | 08 |
| CI/CD and release | Separate environments, trusted artifacts, rollback | 09 |
| Spark | Shuffle, skew, memory and comparison to local SQL | 10 |
| Kafka/streaming | Ordering, delivery semantics, window and checkpoint | 11 |
| Operations/security | SLIs/SLOs, alerts, restore and incident reporting | 12 |
| End-to-end capstone | Reproducible demo, architecture, risk and costs | 13 |

## Ten questions to answer before advancing

1. Why build a pipeline instead of calling the source API directly in every dashboard?
2. What if the source repeats records or changes its schema?
3. What is the grain of each fact table, and which tests detect JOIN fan-out?
4. How do you prevent synthetic demo records from entering a real production dataset?
5. How would you identify the root cause of an incident at 02:00?
6. What is the minimum acceptable quality before publishing a batch?
7. What is the cost of a historical backfill, and what alternatives exist?
8. What can an anonymous user see, and why must RLS and GRANT be checked together?
9. If Spark is slower than DuckDB on a 10 MB file, which question should you investigate?
10. How do you **verify** a restore instead of merely proving that a backup file exists?

## Accurate status vocabulary

| Status | What it actually proves |
| --- | --- |
| `implemented` | Code or design exists, but not necessarily tested |
| `locally-tested` | Relevant tests passed on local synthetic data |
| `integration-tested` | Connected runtime components/databases were tested |
| `deployed` | An authorized remote environment was tested |
| `operationally-validated` | SLOs, alerts, restore, security and costs were actually verified |

Never relabel a local test as a remote deployment. Private progress tracking remains **self-reported** until reviewed, and no automated file marks someone officially certified.
