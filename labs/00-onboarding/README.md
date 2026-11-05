# Stage 00 — Getting Started, Data Flow and Personal Safety

[Module 00](../../curriculum/modules/00.md) · [Learner Handbook](../../docs/LEARNER-HANDBOOK.he.md)

Stage 00 is not just a setup checklist. The learner must demonstrate safe tool use, a minimum Python/Git environment, basic DAG and data-flow understanding, and how to submit **sanitized evidence**.

### Try the grader

~~~bash
python3 labs/00-onboarding/grade.py --reference
python3 labs/00-onboarding/grade.py
~~~

The reference passes **12 tests**. The student starter is deliberately not implemented. The functions accept **synthetic flags** rather than harvesting device information. Do not collect machine username, passwords, env vars or identifying device details to prove readiness. If you choose to run `scripts/system_profile.py`, do so manually and keep its output private.

## Four tasks

1. `readiness`: validate explicit Python version tuple, Git availability and workspace permission flags. Return short, safe issue codes.
2. `pipeline_order`: take a dependency mapping and produce a topological order, rejecting dangling dependencies and cycles.
3. `safe_output_path`: allow a relative evidence path only within an existing workspace; never write or delete a file.
4. `evidence_check`: require a commit reference, exact command, test result and self-reflection, **without** claiming evidence is independently verified.

## Exit gate

- [ ] Student passes all 12 tests with code they wrote.
- [ ] Explains source → validation → curated → serving in own words.
- [ ] Can use Git branch/commit/PR safely without exposing credentials.
- [ ] Creates a clean synthetic example, runs tests and submits a short explanation.
- [ ] Explains the difference between a successful test run and professional competency proof.

**No cloud, Docker or GPU is needed.** A learner who already demonstrates these competencies through an independent diagnostic can shorten the onboarding stage, but should not skip data safety or security.
