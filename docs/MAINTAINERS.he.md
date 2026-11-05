# Public Repository Maintainer Guide

This GitHub repository is an **upstream curriculum template**. Individual learner progress and graded submissions belong in learner-owned repositories or private review workspaces, not in the upstream source tree.

## First-time configuration (if creating another copy)

1. Create a public repository named `data-engineering-mastery` under the approved owner/organization. Avoid auto-generating a duplicate README when importing an existing Git tree.
2. Run repository validation, the unit suite, and the DataPulse tests before publishing:

~~~bash
python3 scripts/validate_repo.py
python3 scripts/audit_program.py
python3 scripts/notebook_smoke.py
python3 -m unittest discover -s tests -v
~~~

3. Protect `main` with required PR review and CI checks; mark the repository as a template if that workflow is appropriate.
4. Use issue labels `learning`, `curriculum`, `bug`, `good first issue`, `security` and `documentation`. Reject submissions containing real credentials or learner personal information.
5. Only tag releases after the relevant gates are verified; update [CHANGELOG](../CHANGELOG.md).
6. Let every learner copy the template into a personal repository. Do **not** grant every student write access to the upstream course.
7. Keep upstream course material separate from private student evidence and optional paid/owner-controlled cloud demos.
8. Recheck official documentation and breaking changes before upgrading Supabase CLI/SDKs, Kafka, Spark, Jupyter or IDE integrations.

## Current scope

All 14 stages have implemented educational labs and graders. Some advanced runtimes are verified **locally and in isolated CI**, but the repository is not an externally certified program or a production data service. A learner pilot, security review and independent assessment remain separate release gates.

## Publishing a new copy

See [the publishing guide](PUBLISHING.he.md). The optional `bash scripts/publish_to_github.sh` command is **user-initiated** and must never be executed against an existing repository without reviewing its checks and confirmation prompts.

## English-first and visual-learning quality checks

Keep lessons, student-facing errors, JSON descriptions, notebook Markdown cells and UI copy in clear English. Maintain working Mermaid diagrams and Markdown links. New contributors should test their Markdown in VS Code preview and open notebooks with the Jupyter visual editor. See [VS Code setup](VS-CODE-LEARNING-SETUP.md).

Never hide a security limitation or change a grading contract for cosmetic reasons.
