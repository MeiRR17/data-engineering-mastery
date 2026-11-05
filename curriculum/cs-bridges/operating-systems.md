# Computer Science Bridge — Operating Systems and Performance

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

Processes, threads, memory limits, file descriptors, page cache, I/O and context switches.

## Think before coding

1. Why does an ETL job run out of RAM when its input file is relatively small?
2. Why can Python/Spark startup dominate a tiny data job?

## Hands-on exercise (15–25 minutes)

Compare streaming a generated file line by line with reading the entire file into memory; record rough memory/time differences without publishing system identifiers.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

What changes if an event dataset exceeds physical RAM and must spill to disk?

## Reference

[Official or technical documentation](https://docs.python.org/3/library/resource.html) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
