# Stage 10 — Big Data & PySpark: Shuffle, Deduplication, Skew

[Stage 10 syllabus](../../curriculum/modules/10.md) · [Stage 09](../09-cicd/README.md)

This stage has two modes designed around the **same correctness contract**. Begin with the lightweight mode even on an ordinary laptop, then advance to **real local PySpark** if Java and enough RAM are available.

<text>Data size is intentionally tiny: the goal is to learn and verify distributed data semantics, not to claim cluster throughput or production-grade performance.</text>

~~~mermaid
flowchart LR
  F[Synthetic JSONL events] --> V[Strict validation + UTC normalization]
  V -->|invalid| Q[Safe reason-code quarantine]
  V -->|valid| B{Choose learning mode}
  B --> L[Light: SHA-256 partitions + Python reduce]
  B --> S[Spark: DataFrame repartition + Window]
  L --> M[Daily-region mart]
  S --> X[Spark groupBy / Shuffle]
  X --> M
  M --> T[Oracle parity and fault tests]
~~~

## System requirements and two learning paths

| Light / all learners | Real PySpark / full mode |
|---|---|
| Python 3.11+ only | Python 3.12, Java 17+ |
| No GPU, Docker or downloads | `pyspark==4.0.5` installed with pip |
| Map/Reduce semantics simulated with stable buckets | Spark executes actual DataFrame transformations |
| 21 reference tests | 9 Spark semantics tests + Spark/Light parity + skew demo |

PySpark 4.0.5 is pinned for reproducibility. Official docs: [Apache Spark Python API](https://spark.apache.org/docs/4.0.5/api/python/) and [Spark installation](https://spark.apache.org/docs/4.0.5/api/python/getting_started/install.html). `pip install pyspark` is a large download; **do not install it on a low-storage machine** just to complete the Light mode.

### Step 1 — light mode

From repository root:

~~~bash
python3 labs/10-spark/grade.py --reference
python3 labs/10-spark/light_cli.py --partitions 2
python3 labs/10-spark/light_cli.py --partitions 7
# Your own implementation (intentionally unfinished):
python3 labs/10-spark/grade.py
~~~

The reference grader must pass **21 tests**. The learner grader fails initially until the `run_light` function in [learner/starter.py](learner/starter.py) is implemented without copying [instructor/reference.py](instructor/reference.py).

The fixture holds **16 input rows**. Four are invalid and quarantined by reason code, 12 are structurally valid, and deterministic latest-update deduplication keeps **9 distinct events**. The six `(UTC day, region)` aggregations count unknown magnitudes separately from measured magnitudes. Some timestamps have UTC offsets; a timestamp shortly after midnight in +02:00 can belong to the **previous UTC date**.

### Step 2 — real Spark mode (optional until hardware allows)

On a computer with Java 17+ and Python 3.12:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install "pyspark==4.0.5"
java -version

# Spark DataFrame plan, executed locally (no cluster):
python3 labs/10-spark/spark_pipeline.py --partitions 2 --explain
python3 labs/10-spark/spark_pipeline.py --partitions 5
python3 labs/10-spark/spark_grade.py --reference

# Learner Spark function, intentionally not implemented:
python3 labs/10-spark/spark_grade.py

# Optional hands-on skew demonstration:
python3 labs/10-spark/skew_demo.py
~~~

Windows learners can use a compatible Python/JDK setup; environment compatibility must be verified individually. Do not run expensive jobs or allocate large worker memory unnecessarily.

**Where Spark work happens:** Python first validates and normalizes the small teaching input. Spark then performs `repartition`, a per-event `row_number` Window with two deterministic ordering keys, `groupBy`, `count`, and `avg`. Output is collected only because the entire fixture is tiny; **real large-scale jobs must write distributed output instead of collecting the full result to the driver**.

## The correctness contract

- `event_id` is the grain. Every source event maps to **at most one** curated row.
- Latest `source_updated_at` wins, regardless of which file line arrives last. Equal timestamps use SHA-256 of canonical normalized content as a deterministic tie-breaker (an educational policy, not a universal business rule).
- All event timestamps are normalized to **UTC before** daily grouping; naive timestamps are rejected.
- A null magnitude counts as an event but does **not** count toward the average denominator. An all-null group returns `None` / SQL NULL, never zero.
- Quarantine reports only stable reason codes: it does not echo the raw invalid row or private fields.
- Changing partition count or input row order must not change the result.

## Data Skew exercise

`skew_demo.py` constructs 1,000 synthetic records, 900 assigned to one hot region. It compares the number of rows landing on each Spark partition when partitioning by `region_code` versus by the high-cardinality `event_id`.

Learner tasks: predict the busiest partition; run the demo; inspect `spark_pipeline.py --explain` for physical Exchanges; explain why a low-cardinality grouping key can create stragglers. Different keys change data movement and may not be valid substitutions in a real distributed computation. **Do not claim one strategy is faster merely because it balances records**; measure actual task time, shuffle bytes, memory and correctness on representative workloads before recommending optimizations.

## Independent tests and transfer

1. Complete the Light mode's `run_light` function and pass all 21 tests without copying the instructor solution.
2. In the full mode, complete `learner/spark_starter.py` and pass 9 Spark tests, including changing partitions and reversing input order.
3. In a personal branch, intentionally remove latest-update deduplication. Predict, observe and explain the count mismatch; restore the correct Window.
4. Add a synthetic event with equal source update timestamp but conflicting magnitude. Define a **business rule** for conflicts and test it.
5. Explain why `groupBy` can cause a Shuffle even if input partitions were balanced by event ID.
6. Discuss **Spark versus SQLite/DuckDB** for small data and the costs of JVM startup, memory and parallel shuffles. A real, controlled DuckDB benchmark is not part of this increment.

**Exit Gate:** learner's own code, two algorithm explanations without AI, Spark execution proof for full mode (or clearly marked not attempted), an unseen transfer case, a PR with red-to-green tests and a discussion of timing/memory tradeoffs.

### Scope and operational limits

- `local[2]` runs on **one machine**; it is not a distributed cluster across machines. No Kafka, streaming state, cloud EMR/Databricks, Parquet storage, real billion-row benchmark, authentication or remote worker orchestration.
- CI tests the instructor reference and local Spark job. It **does not certify the student's understanding**.
- This lab is synthetic-only, with bounded memory and no external data or user machine inventory.
