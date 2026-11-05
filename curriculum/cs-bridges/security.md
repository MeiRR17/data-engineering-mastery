# Computer Science Bridge — Security, Authorization and Trust Boundaries

This short unit connects fundamental computer science to practical Data Engineering. It is not a standalone certification; use it alongside the matching stage lab and explain the invariant in your own words.

## Core concepts

Identity, roles, grants, RLS, least privilege, SQL injection, secret handling and auditability.

## Think before coding

1. Why is a public API key not a substitute for user authorization?
2. How should database roles differ between ingestion, analytics and an anonymous user?

## Hands-on exercise (15–25 minutes)

Define a viewer/operator/admin authorization matrix, write denial tests and verify raw records cannot be served through the public API.

Record the expected outcome *before* running the experiment, then keep a minimal red-to-green test and a short note about what the result cannot prove.

## Unseen transfer question

What happens when a view bypasses expected RLS policies or leaks a service-role token?

## Reference

[Official or technical documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) · [Return to curriculum](../modules/00.md)

**Exit criterion:** show a reproducible synthetic example and defend the failure mode without reading the instructor's answer.
