# Maintainer Roadmap — תוכנית להשלמת המסלול הציבורי

[README](../README.md). **המסמכים החדשים אינם הוכחה שכל מעבדות השלבים הושלמו.** זהו Backlog להרחבה איכותית, עם תנאי קבלה מפורשים.

| Release | תוכן | Gate לפני תיוג |
|---|---|---|
| v0.2.x | README מלא, Visuals, Notebook tutorials 00–03, קישורי וידאו | 4 מחברות רצות, בדיקות יחידה, המחברות ו־DataPulse תקינות, קישורים תקינים |
| v0.3 | Notebook 04–07, SQL/Postgres exercises + automated grader, סביבות light/full | Expected outputs + adversarial tests |
| v0.4 | Supabase isolated project + migrations + security tests | Cloud smoke, RLS negative tests, no secrets in frontend |
| v0.5 | Analytics Engineering/dbt, warehouse/modeling | full data lineage + recomputable metrics |
| v0.6 | Orchestration, incremental/backfills, quality | replay and fault-injection passes |
| v0.7 | CI/CD, monitoring, recovery + costs | deploy, rollback, recovery evidence |
| v0.8 | Spark + Kafka labs light/full alternatives | benchmark + replay tests |
| v0.9 | Capstone grading, community review, multilingual materials | peer review and reproducible portfolio |
| v1.0 | Fully implemented end-to-end curriculum | external review + comprehensive CI + audited docs |

**פיתוח קהילתי:** פתחו Issue עבור תרגיל חדש, ציינו רמת קושי, מטרות, test oracle, dataset provenance, privacy, resource requirements ו־failure cases; לאחר מכן PR אחד עם fixture קטן, הבדיקות, פתרון למדריך בנפרד (לא בנתיב שהלומד אמור לראות) וקישור תיעוד. אין להעלות סרטונים או חומרים מוגנים שהועתקו. גם לגרסה ציבורית 'מושלמת' יש תחזוקה מתמדת, כי כלים ותיעוד משתנים.

### Foundation-labs increment

The Stage 01–03 offline SQL/Python/ETL reference graders and learner starters are under development on a feature branch; **v0.3 is not complete** until notebook 04–07, SQL/PostgreSQL coverage and release gates are implemented and independently reviewed.

### Stage 05 implementation increment (in review)

A standalone PostgreSQL 17 modeling exercise now covers event-grain fact data, versioned region dimension (SCD2), nonoverlap constraint, as-of join, reconciliation, NULL-aware metrics, idempotent reruns and a late-correction scenario. It is tested in a disposable Docker container by a reference solution. This is not a complete dbt project and not a remote Supabase deployment; these remain later acceptance gates.

### Stage 08 development increment (Draft PR)

A local, standard-library HTTP/SQLite read-only serving lab with synthetic Stage 07 data, overview/daily/events/quality JSON routes, safe pagination, stale and blocked-run UX, security headers and black-box loopback tests is available for review. It is not a deployed cloud dashboard, not a production API and not a substitute for real Supabase Auth/RLS verification.

### Stage 09 — Release simulator in the consolidated RC

The offline Stage 09 lesson implements reproducible versioned ZIP bundles, integrity verification, separate simulated environment pointers, health-gated atomic promotion and verified rollback. A dedicated CI job runs the instructor's 26 fault scenarios and end-to-end demo. It does **not** publish a GitHub Release, deploy to real infrastructure, handle real secrets or run irreversible PostgreSQL migrations; those remain explicit acceptance gates for a genuine delivery milestone.

### Stage 10 implementation increment (in RC)

A deterministic pure-Python MapReduce learning fallback (21 instructor-graded scenarios) and a real Java 17 + PySpark 4.0.5 local DataFrame job (9 instructor-graded scenarios, light/Spark parity check, physical-plan explanation and a synthetic skew demonstration). A separate optional CI job installs PySpark and runs locally; running local Spark on one machine is **not** the same as distributed cluster verification. No DuckDB performance benchmark, Kafka, Parquet lake or cloud cluster has been claimed.

### Integrated 00–13 learning coverage — 2026-11-05

The Draft RC now includes 14 stage notebooks, Stage 00–12 labs, a Stage 13 integrated capstone, and an independent review/examination framework. `python3 scripts/audit_program.py` verifies structure, and instructor graders run in CI, including real local PostgreSQL, dbt, Spark and single-broker Kafka. These are *local teaching integrations*, not authorized production deployments. Full release acceptance still requires pilot feedback, examiner review, security review and optional real cloud sandbox proof. See [PROGRAM-READINESS.he.md](PROGRAM-READINESS.he.md).
