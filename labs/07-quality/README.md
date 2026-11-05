# Stage 07 — Data Quality, Data Contracts & Lineage

[Stage 07 syllabus](../../curriculum/modules/07.md) · [Previous lab](../06-orchestration/README.md)

A successful pipeline is not necessarily a correct pipeline. This laboratory teaches **Schema Contract, Schema Drift, Uniqueness, Completeness, Freshness, Quarantine, Atomic Publish and Row Lineage**, using Python 3.11+ and SQLite alone. It makes **no network or cloud calls**, uses synthetic information and does not collect machine identifiers.

The synthetic learning clock is pinned to **2026-01-03 at 12:00 UTC** for reproducible freshness results regardless of today's calendar date.

## Architecture

~~~mermaid
flowchart LR
 A[Synthetic source] --> B[Contract validation]
 B -->|invalid| Q[Quarantine: reason and SHA256]
 B -->|valid| C{Quality gate}
 C -->|blocked| D[Audit only]
 C -->|passed| E[(Curated SQLite)]
 E --> F[Row lineage]
 E --> G[Daily metrics]
~~~

## Run the exercises

~~~bash
python3 labs/07-quality/grade.py --reference
python3 labs/07-quality/grade.py
~~~

The first command checks the **27 instructor-reference scenarios**. The second intentionally fails until you implement the student starter at [starter.py](starter.py). Do not copy the published reference before making your own attempt.

| File | Purpose |
|---|---|
| [contract.json](contract.json) | Versioned schema, allowed fields, validation thresholds |
| [synthetic_events.json](data/synthetic_events.json) | Four public synthetic source events |
| [lineage.json](lineage.json) | Asset dependency graph |
| [starter.py](starter.py) | Six student functions awaiting implementation |
| [grade.py](grade.py) | 27 positive, negative and failure-injection tests |
| [reference.py](instructor/reference.py) | Instructor oracle used by CI |

## Learning sequence

1. Read the contract and predict how an unexpected field or missing ID should be treated. Implement **load_contract** and **validate_row**.
2. Implement **assess_batch**. For malformed rows, retain only the reason code, row index and SHA-256 digest; never persist raw rejected JSON.
3. Implement quality gates for validity ratio, completeness ratio and age-based freshness. A batch can be structurally valid yet too old to publish.
4. Implement **ensure_schema** and **process_batch**: every accepted batch creates an audit record, optionally publishes curated rows, writes row-level lineage and quarantines the rejected records **atomically**.
5. Force a transaction failure before commit and show that neither the data nor its audit is left half-written.
6. Implement **lineage_order**: reject cycles, unknown assets and a dashboard disconnected from its source.
7. Demonstrate replay without double counting, a newer source correction replacing old data and an older update being ignored.
8. Add one new test. Review root cause, remediation and what a production data-quality system would need beyond this lab.

## Quality metrics

| Metric | Calculation | Example threshold |
|---|---|---|
| Valid ratio | Structurally valid records / all records | At least 75% |
| Completeness | Non-null magnitude / structurally valid records | At least 75% |
| Stale ratio | Valid records older than 48h / all valid records | At most 25% |
| Published rows | Actual DB inserts/updates | No duplicate on replay |
| Quarantine | Rejected row counts and safe reason codes | No raw payload retained |

**These numerical thresholds are educational examples, not industry SLAs.** Production policies depend on consumer requirements, data sensitivity and impact.

## No-AI exit test

Explain without assistance: (1) why a pipeline can report SUCCESS while publishing false data; (2) whether Schema Drift should always be rejected; (3) why NULL differs from zero; (4) how to recover an interrupted atomic publish; (5) why a SHA-256 digest is not proof that private source data may be distributed.

Pass the 27 tests using your own implementation, document a red-to-green regression, capture a sanitized command log and open a learner PR. The public repository's CI proves only the **instructor reference** can pass; it does not certify a student's personal competence.

**Scope boundaries:** no production Great Expectations/Soda/DataHub integration, central schema registry, remote metadata service, alert paging, live cloud deployment, real-person data or professional certification.
