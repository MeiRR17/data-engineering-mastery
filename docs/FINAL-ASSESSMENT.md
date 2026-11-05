# Final Assessment — internal Data Engineering competency review

[Course roadmap](ROADMAP.md) · [Scoring rubric](ASSESSMENT.md) · [Capstone](../capstone/README.md)

## What does a complete training pathway mean?

The program supplies instruction, independent implementation tasks, tests, explanations and transfer challenges for **Stages 00–13**: onboarding, SQL, Python, ETL, PostgreSQL, dimensional modeling, orchestration, quality, serving, CI/CD, Spark, Kafka, reliability and capstone.

**Completing this course is not an externally accredited professional qualification or an employment guarantee.** A genuinely evidenced *internal completion statement* requires original learner code, an unseen practical examination, fault-recovery work, a capstone defense and qualified human review. No script in this repository issues credentials.

## Three levels of evidence

| Level | Required evidence | Accurate statement |
| --- | --- | --- |
| Instructor solution works | The reference grader and CI pass | "The instructional exercise was validated" |
| Learner completes a stage | Original code, test results, explanation and PR | "I completed Stage X with reproducible evidence" |
| Learner completes internal program | All 14 gates, capstone, unseen exam and review | "I completed an internally assessed training program" |

## Final examination: 100 points

| Section | Maximum | Required evidence |
| --- | --- | --- |
| A — Independent implementation | **40** | A new event-ingestion solution, SQL/modeling, schema contract, dedup/idempotency and quality measures |
| B — Operations incident | **20** | Triage an unfamiliar pipeline failure, contain harm, repair/recover and write a regression test |
| C — System design | **20** | Compare batch/streaming, PostgreSQL/Supabase, Spark/local SQL, cost, SLO, authorization and scale |
| D — Oral/written defense without AI | **20** | Defend the capstone and explain ACID, event time, Kafka guarantees, SCD2, RLS and recovery |

**Suggested internal pass thresholds:** at least **80/100**, at least 24/40 in A, at least 12/20 in each of B–D, no unresolved P0/P1 security or data-integrity issue, and all stage-specific competency gates satisfied. These are course governance rules, **not a vendor standard**.

## Generate a fresh, unseen transfer exam

An examiner can create a new synthetic case with separate candidate and reviewer-only material:

~~~bash
python3 assessment/generate_transfer.py \
  --seed 20261105 \
  --output /tmp/dem-exam-20261105
~~~

Use a **new, unpredictable seed** and an output directory that does not already exist during real assessment. The generator creates `candidate/` with instructions/data and `reviewer_only/` with a private answer key. Never hand the reviewer-only directory to the student before the exam. This tool generates material; it does not supervise an exam or detect plagiarism.

A reviewer must record the seed, fixture version and candidate commit for auditability.

## Five-dimensional per-stage rubric

Every stage is assessed from 0 to 4 in:
- **Concepts:** what the learner can explain.
- **Independent implementation:** what they can write unaided.
- **Testing/debugging:** how they detect and fix failures.
- **Architecture:** how they justify constraints and trade-offs.
- **Operations/security:** how they protect, monitor and recover the product.

Concepts and implementation should reach **at least 3** in each stage; the integrated Stage 13 capstone should reach **at least 3 in all five dimensions**. A green instructor CI run cannot substitute for these judgments.

## What an examiner should verify

1. The student wrote the solution independently rather than copying an instructor reference.
2. They can predict a failure and explain observed test output.
3. Their code, PR, ADR, commands and tests reproduce on another approved environment.
4. The source data is synthetic or appropriately licensed, and no secrets/PII are exposed.
5. Their description accurately separates *local*, *integration*, *cloud* and *multi-node* evidence.
6. They can solve an **unseen** case and defend architectural choices without AI.

## Evidence package

Keep individual grades, private learner notes and assessment media **out of the public upstream repository**. The review workspace may include:
- `submission.json` following [the example schema](../assessment/submission.example.json).
- Original source code, redacted logs, a PR/commit URL, architecture diagram, at least three ADRs, a demo summary and new transfer-test result.
- Fourteen stage rubric records, reviewer observations and signed/reviewed decisions.
- Score breakdown, strengths, remaining gaps and an individual remediation plan.

The command below verifies the **structure, declared thresholds and local presence of evidence files**. It does not verify authorship, reviewer identity or score truth, and returns at most `ready_for_human_review`:

~~~bash
python3 assessment/evaluate.py /path/to/submission.json
~~~

## Hardware and real runtime evidence

Light-mode Python/SQLite exercises are excellent for fundamentals. They do **not** prove full operational competence with PostgreSQL, dbt, PySpark or a Kafka broker. If the learner postpones one of those full-mode labs, record it as **not yet verified**. Cloud-specific claims require explicit owner-approved sandbox access, negative RLS tests, real remote smoke checks, secret handling, monitoring and restore evidence. Local SQLite tests cannot replace that proof.

## Privacy and completion policy

Only a suitably qualified, specifically appointed examiner can recommend an internal completion statement after reviewing original evidence and an independent exam. Do not publish public "certified learners" lists automatically. Any internal statement should clearly say:

> "Completion of an internally assessed Data Engineering learning program. This is not a recognized professional/vendor accreditation."

The final product-level gate before claiming proven teaching effectiveness is an **independent pilot with a learner unfamiliar with the instructor solutions**, followed by documented remediation and professional content review. Automated tests alone cannot satisfy this gate.
