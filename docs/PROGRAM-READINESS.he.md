# Data Engineering Mastery — readiness ledger for the integrated training path

[Course manifest](training-manifest.json) · [Learner handbook](LEARNER-HANDBOOK.he.md) · [Assessment governance](FINAL-ASSESSMENT.he.md) · [Release Candidate PR](https://github.com/MeiRR17/data-engineering-mastery/pull/15)

## What is implemented in the integrated curriculum?

**All 14 stage curricula (00–13)** have a matching lesson and a lab/capstone, an instructor grader, a deliberately unfinished student starter or independent implementation task, and a guided notebook. The repo includes scripts to validate structural coverage, a synthetic end-to-end capstone, an independent transfer-exam generator and an evidence schema validator.

This is **educational implementation readiness**, not evidence that any specific learner can do the work unaided. The student's green tests, review and external assessment must still happen.

| Group | Stages | Learning proof |
|---|---|---|
| Foundation | 00–03 | Git/readiness, SQL, Python and ETL, synthetic replay, original code |
| Core DB and Analytics | 04–05 | PostgreSQL RLS, actual SQL migrations and temporal Star Schema + dbt |
| Core Operations | 06–09 | Orchestration, data contracts, read-only API/dashboard, simulated CI/CD |
| Advanced Scale and Streaming | 10–11 | PySpark local[2], real local Kafka, offsets, skew, recovery and honest limits |
| Reliability | 12 | SLO evaluation, error budgets, local backup/restore and safe incident drill |
| Portfolio/Assessment | 13 | End-to-end DataPulse capstone, independent exam variants, manual rubric |

## Release quality checks

~~~bash
# Structural path and documentation checks
python3 scripts/validate_repo.py
python3 scripts/audit_program.py

# Run every Stage 04–13 notebook using stdlib only
python3 scripts/notebook_smoke.py

# Run local reference suites and integrated capstone
python3 -m unittest discover -s tests -v
python3 capstone/grade.py --reference
python3 capstone/demo.py

# Optional infrastructure and full-mode checks in GitHub Actions:
# disposable PostgreSQL, dbt, PySpark, Kafka single broker
~~~

**What these checks establish:** assets exist, code examples execute, source fixtures and reference answers produce expected results, and CI exercises service/runtime integrations where configured.

**What they do not establish:** originality of a learner’s solution, that teaching instructions are pedagogically sufficient for a novice, external professional certification, employment readiness, production reliability or cloud service deployment.

## Non-automatable release acceptance gates

1. A learner who did not see instructor reference solutions completes an end-to-end pilot and provides feedback about missing prerequisites, confusing steps and elapsed effort.
2. A qualified reviewer evaluates the **learner's original code**, two new transfer tasks, an operations incident and the 10-minute capstone defense.
3. A security reviewer checks SQL privileges, API exposure, logging/PII policy, pinned dependencies, artifact provenance and whether production claims are appropriately scoped.
4. For a **cloud-deployed** claim: an owner-authorized, isolated Supabase/PostgreSQL sandbox must demonstrate RLS-negative smoke tests, secrets management, identity, monitoring, cost controls and verified restore; this is not run or funded from this repository automatically.
5. For **multi-node big data** or **streaming exactly-once across systems**: additional nonlocal infrastructure and dedicated failure tests are needed. Spark `local[2]` and a single Kafka broker are not equivalent.
6. Maintainer approves a clean Release Candidate, changelog/version, peer review and final documentation audit. The curriculum can be integrated into `main` while these independent external evaluation gates remain open; do not represent it as a certified professional program.

## Release language and claims

- `structure_verified`: all stage guides, notebooks, graders and formal curriculum references exist.
- `ci_green`: specific commit's CI jobs passed.
- `learner_review_ready`: structural score evidence present; evaluator has not authenticated it.
- `learner_assessed`: independent qualified examiner reviewed original work and unseen tasks, with a recorded outcome.
- `deployed`: real approved cloud environment with recorded proof.
- `accredited`: **not claimed** — no external accreditation partnership exists.

Internal completion statements must say "מסלול הכשרה פנימי" and avoid representing a completion certificate as an official vendor or professional credential.

## Next maintenance priorities

The next improvements are qualitative, not simply adding more folders: examine teaching clarity across all 14 modules, broaden unseen evaluation coverage, add controlled performance benchmarking for Spark vs local SQL, complete cloud-based auth/RLS and deployment only with explicit authorized sandbox, and gather real learner feedback. These are acceptance processes, not automatic code tasks.

Last checked in the current development cycle: 2026-11-05; the exact last-green commit must be read from the PR's GitHub Actions before declaring any status.

### Main integration note

Last green pre-merge evidence: [GitHub Actions 41988672097](https://github.com/MeiRR17/data-engineering-mastery/actions/runs/41988672097) at `1fb780d` (8/8). The final documentation-change commit and post-merge `main` CI must be checked separately. Completion of the code-level curriculum does not waive the original human and cloud acceptance gates.
