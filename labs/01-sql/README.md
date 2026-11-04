# Mini Lab 01 — SQL detective

No cloud required. Use SQLite via Python stdlib to practice SQL; switch to PostgreSQL in Stage 01 for `EXPLAIN`, window functions and indexing semantics.

**Mission:** events may be duplicated. Detect duplicate event identifiers, daily summaries and the event with maximum magnitude per location. Explain your aggregation grain and `NULL` behavior.

1. Run: `python3 labs/01-sql/run_lab.py`
2. Read `schema.sql` and write three queries into `notes/` in **your own repository** (not the public upstream).
3. Predict row counts before executing. Try one query with an index and explain what changes.
4. Optional side quest: Why isn't a SQL query a simple `for` loop? Read relational algebra and query planner documentation.

Expected: three rows in seed including a duplicate `e2` update before canonical deduping; `COUNT(*)` counts events, `AVG(magnitude)` ignores `NULL`. This is synthetic data.
