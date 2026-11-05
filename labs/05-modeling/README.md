# Stage 05 — Data Modeling, SCD2 and Analytics Engineering

[Stage 05 syllabus](../../curriculum/modules/05.md) · [DataPulse](../../projects/datapulse/README.md) · [Stage 04](../04-postgres/README.md) · [Visual notebooks](../../notebooks/05_scd2_modeling.ipynb)

## Why this lab exists

Data cleaning is not enough to make analytics trustworthy. A reliable data mart needs **explicit grain, historical meaning, no duplicate counting, and predictable recomputation**. Here you use **real PostgreSQL 17 in a disposable Docker container** (no live Supabase account, external ports or personal data).

~~~mermaid
flowchart LR
  A[(Curated events)] --> B[Event to region mapping]
  C[(SCD2 region history)] --> D[As-of temporal join]
  B --> D
  D --> E[(Fact: one row per event)]
  E --> F[Daily region metrics]
  C --> F
  G[Grain, history, NULL and replay tests] -. verify .-> F
~~~

### Grains and keys

| Table / view | Row grain | Key | Purpose |
| --- | --- | --- | --- |
| Curated events | One accepted source event | `event_id` | Validated upstream event data |
| Event-region mapping | One mapping per event | `event_id` | Synthetic event attribution |
| `dim_region` | One region *version* per validity period | `region_sk` | Preserve historical region names (SCD2) |
| `fact_earthquake` | **Exactly one business event** | `event_id` | Measures and correct historical dimension version |
| `daily_region_metrics` | One UTC date and historical region | Date + region | Consumer-facing derived metrics |

In the fixture, region E changes its name on **January 2, 2026**. An event from January 1 must join to the *old* version, and an event from January 2 to the *new* one. A join on `region_code` alone will multiply facts.

## Start the practical lab

Run from the repository root with Docker available:

~~~bash
docker --version
python3 labs/05-modeling/run_lab.py --reference
python3 labs/05-modeling/run_lab.py
~~~

The first command using `--reference` verifies the instructor solution (also tested in CI). **The student command intentionally fails initially** because the learner starter SQL is incomplete.

You can also keep the original starter untouched and work in your own SQL file:

~~~bash
python3 labs/05-modeling/run_lab.py --answers path/to/my_model.sql
~~~

Without Docker, inspect the SQL and write your attempt; mark the **real PostgreSQL integration test as deferred**, not passed. Static reasoning alone is not equivalent to database execution.

## Student implementation plan

1. Open [setup.sql](setup.sql), identify Source, Dimension and Fact tables and write down the grain of each before editing SQL.
2. Predict the row count if every event joins to every version of its region dimension using only `region_code`.
3. In [starter.sql](starter.sql), load `fact_earthquake` with a valid-time join using the **half-open interval** `[valid_from, valid_to)`.
4. Implement a replay-safe upsert keyed by `event_id`. Avoid unnecessary writes when content is unchanged.
5. Define `analytics.daily_region_metrics` with columns `day_utc`, `region_name`, `total_events`, `known_magnitude_events` and `avg_magnitude`. Use appropriate security-invoker behavior.
6. Re-run the grader and fix the **first failing assertion** before addressing the next.
7. Record grain, as-of join policy, NULL treatment, audit/replay results and a late correction.
8. Open a personal PR showing at least one red-to-green test. Do not include secrets or machine identifiers.

## Verified scenarios

- Four synthetic source events yield four unique fact rows.
- East Sector vs East District is selected by **event time**, not the newest region name.
- A conflicting overlapping SCD2 version is rejected by a PostgreSQL exclusion constraint.
- Daily groups sum to the same four events; NULL magnitudes are excluded from the mean denominator.
- Two runs do not increase the fact count.
- Late correction of a source record changes the fact and aggregate **without inserting a duplicate**.
- The analytics schema remains private to unauthorized anonymous roles.

## Optional Computer Science bridge

**Question:** Why can an index on `region_code` not fix a JOIN whose predicate is missing historical validity conditions?

Draw two region versions and the join cardinality both with and without an as-of condition. Investigate [PostgreSQL range types and exclusion constraints](https://www.postgresql.org/docs/current/rangetypes.html).

## Independent no-AI questions

1. What is grain, and how does a natural key differ from a surrogate key?
2. A late-arriving event describes an old date after a newer dimension version was created. Which version should be selected?
3. Write one query detecting orphan facts and another detecting duplicated fact grain.
4. When is SCD Type 1 more appropriate than Type 2?
5. What would have to change for the model to ingest real geographic source data instead of the synthetic event-to-region mapping?

## Stage 05b — real dbt Core

A **separate dbt project is already included**, with CSV seeds, staging models, a fact model, an analytics mart and generic/custom tests. Open [dbt/README.md](dbt/README.md) for installation and commands. CI runs it with a disposable PostgreSQL database, **not a remote Supabase project**.

**Exit gate:** independent student-authored SQL/dbt, successful database tests, a fixed injected failure, two no-AI questions and a reviewed PR. Passing local modeling tests is not proof of a cloud deployment or a production-grade lakehouse.
