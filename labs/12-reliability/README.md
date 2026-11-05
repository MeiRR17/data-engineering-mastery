# Stage 12 — Production Reliability, Governance & Disaster Recovery

[Stage 12 syllabus](../../curriculum/modules/12.md) · [Stage 11](../11-streaming/README.md) · [Mastery Matrix](../../docs/MASTERY-MATRIX.he.md)

**Learning goal:** move from “the code runs” to “the service is observable, recoverable, safe and cost-aware.” The reference implementation uses Python and an entirely disposable local SQLite database. **It is not a live monitoring system, cloud IAM implementation, or production disaster-recovery test.**

~~~mermaid
flowchart LR
  R[Window run status] --> M[SLO report + error budget]
  F[Event freshness] --> M
  Q[Quality blocks] --> M
  M --> I{Incident?}
  I -->|yes| B[Verified SQLite backup]
  B --> T[Restore to new location]
  T --> V[Row count + SQLite integrity]
  C[Cost scenario] --> D[Risk review and decision]
~~~

## Quickstart

~~~bash
python3 labs/12-reliability/grade.py --reference
python3 labs/12-reliability/incident_drill.py

# Your own incomplete implementation:
python3 labs/12-reliability/grade.py
~~~

All **27 tests** run without a cloud account, Docker, network, telemetry or private data. The student code in `starter.py` starts as `NotImplementedError` and is intentionally independent of the instructor reference.

## What you will build

| Component | Engineering contract |
|---|---|
| SLI and SLO evaluation | Run success ratio; data freshness against an aware UTC clock; blocked-data quality ratio |
| Error budget | Explicit target and observed failed windows; remaining budget cannot be negative |
| Runbook trigger | Report issues for stale/future/empty datasets and unavailable/blocked runs |
| RBAC | Explicit viewer/operator/admin role-action matrix; unknown actions denied |
| Backup integrity | Online SQLite backup with SHA-256, row count and `pragma integrity_check` |
| Safe restore | Restore only into a **new** file; never overwrite a live database |
| Cost planning | Explain storage GiB, estimated retained bytes, compute hours and missing costs |

### Lab SLO contract

The included [policy.json](policy.json) is **example policy**, not an industry SLA. You must be able to distinguish:
- **Availability SLI:** proportion of successfully completed run windows; a missing window and a failed window have different interpretation unless your denominator definition includes scheduled windows.
- **Freshness:** age of last accepted event measured against an agreed UTC clock. A healthy process with old data is not a healthy data product.
- **Quality:** a Batch blocked by contract validation did *not* publish unreliable rows, which is good, but it is still an availability/quality incident to consumers.
- **Error budget:** the number of allowed unsuccessful windows given an SLO target. Discuss rounding and window duration assumptions.

The fixed incident clock in this exercise is 3 January 2026, 12:00 UTC, to keep tests deterministic.

## The recovery drill

Run `incident_drill.py`. It simulates three run windows (success/failure/quality blocked) and a stale event. The script then builds a verified SQLite backup, intentionally deletes a **synthetic** event from a temporary database, and restores the backup to a *new file*. The drill verifies data count and integrity.

A real production restore additionally needs PITR/replay, encryption at rest, retention and access restrictions, secret rotation, protected key management, measured RPO/RTO, cross-region survivability and manual incident review.

### Student incident report template

- **Incident ID / time / data product:** synthetic, never paste machine user details.
- **Detection:** exact SLI/SLO breach and evidence of its impact.
- **Scope:** upstream source, ETL, warehouse and consumer-facing freshness.
- **Containment:** block bad releases/queries, preserve verified good checkpoints.
- **Recovery:** restore into isolated environment, run integrity and reconciliation, replay missing windows.
- **Verification:** demonstrate count equality and no secret leakage; measure RPO/RTO honestly.
- **Prevent recurrence:** add a regression test, a runbook decision gate and alerts.
- **Follow-up:** one clear owner and next checkpoint (as an exercise, no real paging).

## Security and governance exercises

1. Explain why a `viewer` role cannot call `restore_to_new`, and why a service-role token must never appear in client-side JavaScript.
2. Enumerate PII and data classification in a hypothetical dataset, propose retention and deletion policy. Do **not** upload real PII to the lab.
3. Design a permissions matrix with separation of duties between ingestion, analytics consumers and deploy operators. Explain what real RLS and IAM add beyond this local action authorization.
4. Draw a Threat Model for artifact poisoning, leaked secrets, stale reporting, corrupted backups and insider misuse.
5. Produce a **risk register**: likelihood 1–5, impact 1–5, owner, detection, mitigation, residual risk.
6. Compute a monthly cost for 10× and 100× the event rate, note egress, replication, Kafka, logs and backup fees **not included** in the simple formula.
7. Design an actual RPO/RTO drill for a disposable PostgreSQL/Supabase training project; record precisely which checks would require a connected cloud account and approval.

## No-AI transfer exam

Your colleague wakes you up at 02:00 and reports that the dashboard shows data 36 hours old, while CI is green. Explain:
- which indicators you inspect **first**;
- how you identify the last good ingestion/quality/checkpoint;
- when to stop consumers versus replay a bounded backfill;
- whether to restore from backup, and **why backup existence alone is insufficient**;
- how to ensure recovery does not expose a private dataset or overwrite live state.

**Exit Gate:** all 27 grader scenarios pass on your own code, the incident drill works, you supply a red-to-green fault report, SLO definitions, RPO/RTO exercise, risk register, cost assumptions and a reviewed PR.

**Unverified:** real alert routing, IAM/RLS in Supabase, encrypted production backup/restore, multi-region failover, external cloud bill, disaster-recovery RPO/RTO guarantees. Do not mark such capabilities as deployed from this lab.
