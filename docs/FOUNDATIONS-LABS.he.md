# Foundations Labs — a guided SQL, Python and ETL sequence

[Home](../README.md) · [Roadmap](ROADMAP.he.md) · [Assessment](ASSESSMENT.md)

**Documentation is not the same as competence.** These are three real graded labs sharing a single synthetic event source and explaining what happens between an upstream feed and a trusted database.

~~~mermaid
flowchart LR
  A[Stage 01: SQL and event identity] --> B[Stage 02: Python validation]
  B --> C[Stage 03: Replay-safe ETL]
  C --> D[Stage 04: Isolated PostgreSQL]
  E[Algorithms, types, ACID and HTTP failures] -. explain .-> B
  E -. explain .-> C
~~~

## Prerequisites

Python 3.11+ and Git are enough to start. There is no requirement for Docker, a cloud account, a paid ChatGPT account or GPU. Source data is synthetic, and the early SQL exercises run on in-memory SQLite.

## Exact start commands

From your personal copy of the repository:

~~~bash
python3 scripts/validate_repo.py
python3 labs/01-sql/run_lab.py
python3 labs/01-sql/grade.py
~~~

`grade.py` is **expected to fail initially**: open `labs/01-sql/tasks.sql` and implement the [SQL tasks](../labs/01-sql/README.md). Then continue with [Python](../labs/02-python/README.md) and [ETL](../labs/03-etl/README.md):

~~~bash
python3 labs/02-python/grade.py
python3 labs/03-etl/grade.py
~~~

Each lab has two grading modes: **learner mode** (without arguments, tests your unfinished starter) and **maintainer mode** (`--reference`, verifies that the reference and tests still agree). The reference is visible for source review but should **not** be copied as proof of independent learning.

## Suggested four-part sequence

| Learning block | Core topic | Demonstrated evidence |
| --- | --- | --- |
| 1 | SQL, NULL, aggregates, windows and deduplication | Four correct queries on two datasets; explanation of grain |
| 2 | Python parsing, GeoJSON, timestamps, validation | Six edge cases plus an independently written parser |
| 3 | ETL transactions, replay, quarantine and failure injection | Seven integration cases and a reproduced incident |
| 4 | Independent extension, code review and PostgreSQL preparation | PR, no-AI explanation and an unseen transfer problem |

The sequence is competency-based. Spend longer on a failed prerequisite rather than advancing to satisfy a calendar deadline.

## Every lesson follows the same method

1. Present one failure and ask for a prediction.
2. Require an initial independent coding attempt.
3. Offer progressively smaller hints when necessary.
4. Inspect actual test output and require a causal explanation.
5. Connect the result to B-trees, types, transactions, isolation or idempotency.
6. Test a **new** case, not the same one solved in the reference.
7. Record a PR, redacted test evidence, limitations and a next action.

## Must-understand failure cases

| Failure | Required reasoning |
| --- | --- |
| Duplicate source row | Count business events, not arbitrary JOIN rows |
| NULL magnitude | Explain the difference between `COUNT(*)` and `COUNT(column)` |
| Text, NaN or boolean in numeric field | Reject explicitly; do not silently coerce |
| Mixed timezones | Normalize to UTC and preserve event time |
| Unexpected API field | Follow the versioned schema contract |
| Repeated batch | Replay does not multiply events |
| Older source correction arrives last | Old revision cannot overwrite a new revision |
| Malformed record within valid data | Safe quarantine and explainable quality metrics |
| Excessive invalid fraction | Block publication atomically |
| Crash before commit | No partially published rows or checkpoints |

**Completion gate:** the learner's own code passes all three labs; their personal PR contains reproducible commands, two independent explanation questions, a new test and no secrets. Only a qualified independent assessment can turn self-reported progress into verified competency.

The full 14-stage program extends beyond these foundations to PostgreSQL, dbt, Spark, Kafka and the [capstone](../capstone/README.md).
