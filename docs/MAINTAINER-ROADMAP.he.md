# Maintainer Roadmap — historical releases and current acceptance gates

[Home](../README.md) · [Program readiness](PROGRAM-READINESS.he.md) · [Assessment](FINAL-ASSESSMENT.he.md)

The following **release labels are historical planning milestones**, not a claim that the related products were deployed or externally certified. All 14 instructional stages now have tutorials, labs, reference tests and an integrated capstone.

| Planning milestone | Educational increment | Evidence still needed before a corresponding release claim |
| --- | --- | --- |
| v0.2.x | README, visuals and the first four notebooks | Content, notebook and local tests |
| v0.3 | Guided notebooks and SQL/Python/Postgres labs | Instructor graders and learner tasks |
| v0.4 | Supabase cloud isolation and migration security | Authorized cloud smoke and negative RLS tests |
| v0.5 | Analytics Engineering, star schema and dbt | Reconciliation, lineage and model tests |
| v0.6 | Orchestration, backfills and quality | Deterministic replay and injected failures |
| v0.7 | CI/CD, monitoring, recovery and cost analysis | Deployment, rollback and restore proof |
| v0.8 | Spark and Kafka light/full learning modes | Runtime correctness and representative benchmarks |
| v0.9 | Capstone, community review, English materials | Independent solution and reviewer evidence |
| v1.0 | Complete reviewed learning program | Comprehensive CI, qualified learner pilot and content review |

## Implemented course infrastructure

The integrated course currently includes:
- All 14 stages, guided notebooks and separate student/reference paths.
- Local PostgreSQL 17 and dbt integration, SCD2 historical joins and NULL-aware metrics.
- Orchestration, data quality, lineage and read-only analytics API/dashboard.
- Local release packaging, synthetic promotion/rollback, Stage 10 PySpark and a disposable Kafka broker.
- Stage 12 incident, SLO, backup/restore and governance exercises.
- A cross-stage DataPulse capstone and an independently reviewed, separately seeded assessment framework.

These **prove the instructor code is executable under the tested environments**, not that a novice learner or any specific student has mastered all the tasks.

## Contribution and review process

1. Open an issue stating the learner level, business question, dataset provenance, privacy constraints, runtime requirements and at least one failure mode.
2. Submit a focused PR with synthetic fixtures, an unfinished learner starter, a separate instructor reference and black-box tests.
3. Review code safety, test determinism, portability, licensing, secrets, local links and English readability.
4. Require a green CI run on the exact review commit; independent student evidence is reviewed separately.
5. Do not host copied copyrighted training videos or upload real personal information.

## Remaining gates

- **Teaching:** run a complete pilot with a learner unfamiliar with the instructor references; measure blockers and learning outcomes.
- **Security:** review SQL grants/RLS, API exposure, dependencies, provenance and secret boundaries.
- **Cloud:** only a separately authorized and budgeted sandbox can verify authenticated cloud access, restore, monitoring and production-like deployment.
- **Scaling:** single-host Spark and single-node Kafka do not demonstrate multi-node throughput or cross-system exactly-once.
- **Credentials:** no external accreditation has been granted, and CI must never issue certificates.

## Versioning discipline

Use semantic versions and a changelog after the appropriate acceptance gates. Keep test artifacts and a clear commit SHA. The English-language conversion does not change graded business semantics; if it does change a task, update its grader and assessment description in the same PR.

See [the program readiness ledger](PROGRAM-READINESS.he.md) for supported claims and unverified work.
