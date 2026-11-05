# Computer Science Bridge — Networking, HTTP and APIs

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

TCP/TLS, HTTP status codes, timeouts, retries, rate limiting, authentication and API contracts.

## Think before coding

1. Why should a 429 response be treated differently from a malformed 400 request?
2. What happens when a request succeeds but the response never reaches the client?

## Hands-on exercise (15–25 minutes)

Mock HTTP 429/500/timeouts with bounded exponential backoff; prove retries do not duplicate persisted rows.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

How would you constrain a public GET endpoint's parameters to prevent expensive or unsafe queries?

## Reference

[Official or technical documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
