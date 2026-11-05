# Computer Science Bridge — Databases and Transactions

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

ACID, MVCC, indexes, locks, write-ahead logging and query planning.

## Think before coding

1. What happens when a process crashes between writing a row and committing its checkpoint?
2. Why can snapshot isolation differ from serializable behavior?

## Hands-on exercise (15–25 minutes)

Use SQLite to execute a transaction, inject a failure and verify the sink and checkpoint roll back together.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

Why does a transactional database not automatically make a multi-service pipeline exactly once?

## Reference

[Official or technical documentation](https://www.postgresql.org/docs/current/tutorial-transactions.html) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
