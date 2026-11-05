# DataPulse — one evolving learning product

DataPulse is a project ladder, not a disconnected series of demos. Each new stage adds an explicit engineering challenge and a testable quality or recovery property.

| Stage | What you add | Evidence for completion |
| --- | --- | --- |
| 01 | SQL windows, indexes and query plans | Correct query and justified plan |
| 02 | Strict Python parser, types and errors | Three learner-authored edge-case tests |
| 03 | SQLite ingest and upsert | Replay cannot increase event count |
| 04 | PostgreSQL migration, RLS and optional Supabase sandbox | Approved read-only public access and secret isolation |
| 05 | Fact/dimension analytical mart | Source-to-mart reconciliation and historical joins |
| 06 | DAG and retry/backfill | Controlled failure, idempotent recovery |
| 07 | Contract, quarantine and lineage | Invalid data blocked with safe evidence |
| 08 | Dashboard and KPI contract | Accurate metric and read-only API checks |
| 09 | Release engineering and rollback | Verified promotion and recovery |
| 10 | PySpark local processing | Measured partitioning and correct aggregates |
| 11 | Kafka broker exercise | Duplicate, ordering, offset and restart tests |
| 12 | SLO and incident response | Restored dataset and incident evidence |
| 13 | Integrated capstone | Original code, demo, ADRs, PR and technical write-up |

**Do not copy an AI agent's solution without understanding it.** The learner must design schemas, write code, run tests, document decisions and defend the reasons for each component. This project is synthetic unless an independent authorized deployment is specifically verified.
