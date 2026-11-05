# Troubleshooting — learn the root cause, not just the workaround

[Home](../README.md) · [Visual VS Code setup](VS-CODE-LEARNING-SETUP.md)

**Rule:** never run a destructive command suggested by AI without reading and understanding it. Protect source data and credentials. A successful fix should include **why the failure happened** and a regression test.

## Five-step diagnostic protocol

1. Record **Expected vs Actual** and the failing data stage: Extract, Validate, Transform, Load or Serve.
2. Preserve an error message **without** tokens, personal paths, usernames or confidential payloads.
3. Reproduce with the smallest synthetic fixture; do not repeatedly experiment on production data.
4. Check versions, configuration, schema, network, permissions and logs, changing one variable at a time.
5. Compare multiple hypotheses, establish the root cause, and add a test that prevents recurrence.

## Editor and environment problems

| Symptom | Safe diagnosis | First action |
| --- | --- | --- |
| `python3: command not found` | Check `python --version` or `py -3 --version` | Install official Python; Windows often uses `py -3` |
| `ModuleNotFoundError` | Check cwd, interpreter and virtual environment | Activate the project venv; install documented dependencies only |
| Wrong Git branch | `git status` and `git branch --show-current` | Check the cloned root; never delete `.git` to fix confusion |
| `roadmap.py init` fails | `learner/progress.json` already exists | Preserve it and run `status`; initialization is one-time |
| `No module named datapulse` | Verify repository root and `PYTHONPATH` | Use the exact DataPulse lab command |
| `.md` shows raw text | VS Code is in the text editor | Press Cmd/Ctrl+Shift+V for Markdown preview |
| `.ipynb` shows JSON | Wrong editor association | **Reopen Editor With... → Jupyter Notebook** |
| Notebook cannot run | No kernel selected / missing `ipykernel` | Choose a Python environment and install kernel support |
| Notebook video is blank | iframe/network disabled | Use the original YouTube link; code exercises still work |
| Docker will not start | `docker info`, memory availability | Start Docker or use the Light SQLite path |
| Port already in use | Another process owns the port | Choose an unused port; do not kill someone else's service |

## Data Engineering incidents

| Symptom | Check | Repair principle |
| --- | --- | --- |
| HTTP 429 | `Retry-After` and rate limits | Bounded backoff; no infinite loop |
| Timeout | Connect/read timeout, latency | Time-bounded retries and pagination |
| Schema drift | Field/type differences | Versioned contract, validation and quarantine |
| Missing events | Watermarks, timestamps and pagination | Bounded overlap, dedup and late-correction handling |
| Duplicates | Business key and run ID | Idempotent upsert |
| Invalid data reaches curated layer | Business invariants | Assertions at ingest and publishing |
| Incorrect NULL or date | Parsing, locale and timezone | Explicit type and UTC normalization |
| Wrong SQL count | JOIN grain and group cardinality | Detect one-to-many fan-out before aggregate |
| Slow SQL | Query plan on isolated dev data | Baseline before adding indexes/partitions |
| Partial batch committed | Transactions and checkpoints | Atomic state and replay safety |
| DAG stalls | Dependencies and worker logs | Bounded retries, alert and scoped backfill |
| Spark runs out of memory | Shuffle, spill and partition load | Sample, measure and limit concurrency |
| Kafka replays events | Consumer group offsets | Replay-safe sink, explicit offset policy |
| Late event changes metric | Event vs processing time | Documented allowed lateness and correction |
| Stale dashboard | Source vs processed timestamps | Freshness SLI and clear user-visible warning |

## Cloud, GitHub and security

| Symptom | Investigate |
| --- | --- |
| REST table inaccessible | GRANT, RLS, Data API exposure, session |
| `permission denied` | Role and row policies; do **not** disable RLS as a workaround |
| View leaks raw rows | Definer behavior, `security_invoker` and grants |
| Secret appears in browser | Revoke/rotate immediately and move privileged credentials server-side |
| Supabase CLI command missing | Inspect installed version and official `--help` |
| Migration missing | Review migration history; never blindly remote-reset |
| GitHub CI fails | Reproduce the exact failing job and pinned dependency |
| No available GitHub write action | Check connector permissions, then use an authorized local workflow |
| Cloud costs grow | Identify authorized compute/storage/egress and enforce a budget |
| Secret committed to Git | Rotate, investigate exposure and clean history safely with owner review |

## Useful issue report template

~~~text
Expected behavior:
Observed behavior:
Failing stage:
Smallest synthetic reproduction:
Runtime versions / hardware tier (light/moderate/full only):
What I already tried:
Potential side effects of the proposed fix:
Redacted logs and exact test command:
Root cause and new regression test:
~~~

If you copied a fix without understanding it, explain the failure and write an independent test before marking the exercise complete.
