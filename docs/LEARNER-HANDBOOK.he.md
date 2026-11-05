# Learner Handbook — from software engineer to an operational data product

[Home](../README.md) · [Visual VS Code setup](VS-CODE-LEARNING-SETUP.md) · [Assessment](FINAL-ASSESSMENT.he.md)

This is the learner's **runbook**, not a shortcut for making an AI agent do every exercise. Prior software engineering experience can shorten genuinely understood topics, but prerequisites should be assessed rather than skipped automatically.

## Day 0 — set up without a cloud account

1. Create your own GitHub account, enable two-factor authentication, and install Git, Python 3.11+ and Visual Studio Code.
2. Use the repository template or clone the source. Open the **whole project folder** in VS Code; verify that you can see `scripts/` and `curriculum/`.
3. Install the recommended [Markdown and Jupyter extensions](VS-CODE-LEARNING-SETUP.md) to open `.md` as formatted pages and `.ipynb` as visual interactive cells.
4. Check `python3 --version` and `git --version`. Optionally run `python3 scripts/system_profile.py`. Never run arbitrary `sudo` commands to make a tutorial work.
5. Run the curriculum audit and local tests:

~~~bash
python3 scripts/validate_repo.py
python3 scripts/audit_program.py
python3 -m unittest discover -s tests -v
~~~

6. Initialize your **private, local** progress record once:

~~~bash
python3 scripts/roadmap.py init --alias learner
python3 scripts/roadmap.py status
python3 scripts/roadmap.py next
python3 scripts/roadmap.py start 00
~~~

7. Open [Notebook 00](../notebooks/00_data_journey.ipynb), predict the outputs and run the cells. If you do not have a notebook kernel, use the documented VS Code setup before installing heavyweight data services.
8. Create a personal issue titled `Stage 00 — setup and diagnostic` and a branch such as `learn/00-foundations`.
9. If you use ChatGPT as a tutor, share only the safe stage context and the [English mentor instructions](../prompts/MASTER-AGENT.en.md). Do not share passwords, full system profiles or private learner reflections.

## Where to work

| Directory | Your responsibility |
| --- | --- |
| `README.md` | Understand the roadmap and open the next lesson |
| `curriculum/modules/XX.md` | Follow objectives, prerequisites and exit criteria |
| `curriculum/cs-bridges/` | Revisit the relevant algorithms/OS/networking concepts |
| `notebooks/` | Predict and run visual tutorials with synthetic data |
| `labs/` | Implement independent starters, tests and failure investigations |
| `projects/datapulse/` | Grow the primary event-to-analytics product |
| `capstone/` | Combine previous stages into a defensible portfolio project |
| `scripts/` | Check environment, select the next activity and validate files |
| `learner/progress.json` | Keep **private and local**, never submit unredacted |
| `docs/` | Read operational instructions, deployment boundaries and review rubrics |
| `.github/` | Review CI/PR configuration before proposing changes |

## Diagnostic and learning plan

The mentor uses five 0–4 dimensions: conceptual understanding, independent implementation, testing/debugging, architecture and operations/security. Check SQL JOIN/GROUP BY/NULL, Python modules/exceptions/tests, Linux process/files/environment, HTTP/retries, database keys/indexes/ACID, Git PRs and algorithmic complexity.

For each session, record a **problem**, expected outcome, independent attempt, exact command, test result, brief CS bridge and one transfer question. The mentor gives graduated hints (direction → technique → partial example) only when needed.

Choose exercises by available resources: **Light** (SQLite, notebook, Python), **Moderate** (optional Docker/PostgreSQL/dbt), **Full** (optional real local Spark/Kafka). A GPU is not needed. Corporate devices and cloud environments must follow local policy and cost approval.

## Eleven-step workflow for every stage

1. Define who consumes the data and the expected accuracy, freshness, cost and security.
2. Draw source → ingest → validation → storage → consumer; mark assumptions.
3. Define Done: deliverables, schema, at least one metric, negative tests, replay behavior and documentation.
4. Start with the smallest working system, often Python/SQLite/PostgreSQL before Spark/Kafka.
5. Create a personal issue, `learn/XX-topic` branch and focused commits.
6. Attempt the task **independently for 20–30 minutes** before asking for a full answer.
7. Run one Computer Science bridge experiment relevant to the failure.
8. Test happy paths **and** duplicates, NULL, invalid input, retry, permission denial and recovery.
9. Check source provenance, business keys, event timestamps and lineage.
10. Review complexity, cost, privacy, secrets, compatibility and rollback alternatives.
11. Explain the result without AI, solve an unseen variation, obtain review, then record only **self-reported** completion until an independent examiner approves it.

## A 75-minute practice session

| Minute | Activity | Reason |
| --- | --- | --- |
| 0–8 | Interesting broken result or slow query | Build curiosity and diagnostic skill |
| 8–23 | Independent attempt and assumptions | Avoid dependence on generated solutions |
| 23–35 | Focused video/documentation and CS bridge | Learn just enough theory |
| 35–55 | Write code and run tests | Learn by implementation |
| 55–65 | Safe failure injection and repair | Avoid happy-path-only learning |
| 65–75 | Explain, record and choose tomorrow's task | Strengthen retention and transfer |

On a shorter 25-minute day, do **one problem, one experiment and one explanation** instead of rushing through multiple new technologies.

## Failure scenarios you must master

| Incident | Evidence of competence |
| --- | --- |
| API responds 429/503 | Bounded backoff, timeouts and no hidden loss |
| Repeated source rows | Unique business keys and replay-safe upsert |
| Missing JSON field / schema drift | Contract test and safe quarantine |
| Mixed timezone timestamps | Correct aware datetime normalization to UTC |
| NULL, duplicates or outliers | Quality policy with explicit numerator/denominator |
| Raw dataset missing | Retention/lineage plan and verifiable reproducibility |
| Crash after partial processing | Atomic transaction and recovery checkpoint |
| Slow SQL | EXPLAIN, baseline and workload-specific benchmark |
| Inflated fact table | Correct grain and JOIN cardinality tests |
| DAG task runs twice | Idempotent execution and concurrency policy |
| Unbounded backfill | Partition/time range and cost limits |
| Out-of-order Kafka event | Event time, deduplication and lateness policy |
| Slow Spark job | Inspect shuffle/spill/skew and collect measurements |
| Dashboard leaks data | Negative authorization tests and private schemas |
| Secret committed to Git | Immediate revoke/rotation and safe incident response |
| Uncontrolled cloud bill | Budget alerts, environment isolation and cleanup |
| Breaking migration | Versioning, compatible rollout and restore strategy |
| Data loss / disaster | Verified backup and isolated restore rehearsal |
| Green tests but wrong KPI | Reconcile expected business counts |
| Missing observability | Freshness/volume/error SLIs and useful alert thresholds |

Use the [troubleshooting guide](TROUBLESHOOTING.he.md) to investigate specific errors.

## Deploying a project later (not required to start)

1. **Local:** fixture-based run, tests, schema and dry-run behavior.
2. **Isolated dev:** optional owner-approved Supabase training project with cost review.
3. **Migrations:** versioned SQL and negative permission tests.
4. **Secure app:** secrets stay server-side; browser has only appropriate public keys and authorized queries.
5. **Delivery:** a separate runner, bounded retries, checks and no deploy secrets in untrusted PR CI.
6. **Operations:** real monitoring, rollback, backups, restore rehearsal and explicit budgets.

Never use destructive remote reset commands against important data. Check the actual Supabase CLI version and its help output first. See the [deployment checklist](../projects/datapulse/DEPLOYMENT-CHECKLIST.he.md) and [official Supabase guidance](https://supabase.com/docs/guides/local-development/cli-workflows).

## Stage completion and portfolio

A learner PR should include problem, source/fixture, schema, reproducible commands, expected and actual outputs, positive and negative tests, risks, cost/security limits, rollback approach, a broken-then-repaired test and two independent explanations.

After Stage 13, select one specialization rather than claiming mastery of everything: analytics/dbt, streaming/Kafka, data platform/lakehouse, AI data pipelines or reliability/architecture. Real work experience and qualified review remain distinct from course completion.
