# Stage 01 — SQL Detective: real questions, not memorized syntax

[Back to foundations](../../docs/FOUNDATIONS-LABS.he.md) · [Stage 01](../../curriculum/modules/01.md)

## Mission
An API delivers multiple versions of one earthquake. The product manager asks how many **distinct events** happened each day, whether duplicates exist, and which earthquake was strongest in each location. Count rows before running queries; decide what constitutes a *fact*.

The included SQLite dataset is **synthetic** and runs offline. It intentionally contains duplicate `e2` and a `NULL` magnitude. PostgreSQL and its EXPLAIN ANALYZE are a later extension; SQLite is the entry-level training environment.

```bash
python3 labs/01-sql/run_lab.py
python3 labs/01-sql/grade.py
```

The second command **fails by design** until you edit `labs/01-sql/tasks.sql`. Do not edit grader, fixture or `instructor/` to make the test pass.

## Four queries to implement
1. `duplicates`: `event_id, versions` — which IDs have multiple rows?
2. `latest`: `event_id, location, occurred_on, magnitude, updated_at` — choose **one** version per event using newest `updated_at`; break ties by greatest `row_id`.
3. `daily`: `occurred_on, event_count, avg_magnitude` — summaries from the latest versions, using correct NULL semantics. Round the average to three decimals.
4. `strongest`: `location, event_id, magnitude` — strongest non-NULL earthquake in each location; break magnitude ties by smallest event ID.

Your output order is unimportant, but **column order and row values matter**. The grader checks both the original and a second dataset with extra updates and an equal-timestamp tie.

## Guided investigation
- Before coding, predict whether `COUNT(*)` and `COUNT(magnitude)` return the same result.
- Try a plain `GROUP BY` and explain why it may select the wrong version.
- Learn window functions: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.
- Explain the difference between `WHERE`, `HAVING`, and a CTE.
- Compare `EXPLAIN QUERY PLAN SELECT ...` before/after an index in a **separate local experiment**, and explain why an index is not always faster.

## Passing gate (self-reported, subject to review)
- `python3 labs/01-sql/grade.py` returns 0 for **all 8 task/dataset combinations**.
- Show query output, one execution plan comparison and a short explanation of grouping grain and NULLs.
- Without AI: why is `MAX(updated_at)` alone not sufficient when timestamps tie?
- Make a fresh query for a new business question and explain it to a reviewer.

Only after your own attempt, instructors can inspect `instructor/reference.sql`. Do not copy it into your personal submission; the ability to solve a transfer problem independently matters more than a green indicator.
