# Computer Science Bridge — Distributed Systems and Delivery Guarantees

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

Partitions, logical clocks, leader election, consistency, retries, idempotency and at-least-once delivery.

## Think before coding

1. What can a consumer safely infer after a timeout with no acknowledgement?
2. How do partition ordering guarantees differ from global ordering?

## Hands-on exercise (15–25 minutes)

Simulate duplicate messages, a late correction and a crash after committing to SQLite; add a deterministic replay test.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

What coordination is required to atomically commit both Kafka offsets and an external sink?

## Reference

[Official or technical documentation](https://kafka.apache.org/documentation/) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
