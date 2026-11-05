# Computer Science Bridge — Software Architecture and System Design

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

Modularity, data contracts, failure domains, coupling, DAGs, SLIs and cost/latency tradeoffs.

## Think before coding

1. Where should validation happen: ingestion, warehouse or serving?
2. Can failure in one stage block unrelated consumers?

## Hands-on exercise (15–25 minutes)

Draw a source → validate → curate → serve architecture and mark which component owns retries, secrets and public access.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

How would you change the design if the source throughput grew 100×?

## Reference

[Official or technical documentation](https://martinfowler.com/architecture/) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
