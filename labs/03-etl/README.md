# Stage 03 — Transactional SQLite ETL: Replay, Crash, Quarantine

[Back to foundations](../../docs/FOUNDATIONS-LABS.he.md) · [Stage 03](../../curriculum/modules/03.md)

## Incident report
The feed was ingested twice after a network timeout. A stale update arrived afterwards. One row contained an invalid coordinate. Halfway through processing another batch, the process crashed. Can the analytics database remain correct?

Edit `labs/03-etl/starter.py`. Start with SQLite (`sqlite3` from the Python standard library), **not** Supabase: learn transaction semantics locally first.

```bash
python3 labs/03-etl/grade.py
```

The starter intentionally fails until your solution meets the contract.

## Public interface

```python
init_db(conn) -> None
load_batch(conn, events, max_reject_fraction=0.5, fail_after=None) -> dict
# returns {"written": int, "rejected": int, "unchanged": int}
```

`events` is a list of **normalized dicts** as returned by Stage 02. Each includes `event_id`, `observed_at`, `source_updated_at`, `magnitude`, `place`, `latitude`, `longitude`. Use timezone-aware ISO timestamps, normalized to UTC.

## Data model
- `events`: one row per `event_id`, primary key; preserve latest `source_updated_at` only.
- `quarantine`: fingerprint (SHA-256 of canonical, safe serialized bad input) and reason, with a uniqueness constraint. Store **no raw bad payload**.
- `init_db` is safe to run twice and creates both tables.

## Required behavior
1. First load inserts rows. Same batch again writes **zero** rows and does not expand the table.
2. An event with a *newer* source timestamp updates the stored row. A stale or equal-timestamp replay does not overwrite it.
3. Invalid IDs, coordinates, magnitude or timestamps are rejected; those rows are quarantined without publishing bad analytics records.
4. If `rejected / batch_size > max_reject_fraction`, abort **the entire batch**, including quarantine changes, and raise `DataQualityError`.
5. If `fail_after=0`, raise a simulated crash **after the first write but before commit**; rollback must leave no partial writes. This is a test switch, not a production knob.
6. All writes of each batch are atomic. Never concatenate external input into SQL. Use parameterized queries.
7. Retry of the same invalid row must not create duplicate quarantine entries.

## Procedure
- Draw a transaction boundary before writing code.
- Write two hypotheses: what does an Upsert accomplish, and what does it **not** guarantee?
- Start with simple insert, then add `ON CONFLICT` and a timestamp condition.
- Run the grader, introduce a crash, inspect the database after rollback.
- Explain why `source_updated_at` differs from `ingested_at`. What would change for late-arriving data?
- Demonstrate why the operation is idempotent *at the published data layer* and discuss storage costs of deduping bad inputs.

## Exit gate
7 integration cases pass, including the simulated crash, plus one independently designed fault injection. Submit PR with reproducible tests and a short incident report (hypothesis, evidence, root cause, prevention).

Instructors: `python3 labs/03-etl/grade.py --reference` verifies the implementation in `instructor/reference.py`. Learners should not copy it; write and explain their own code.
