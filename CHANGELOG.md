# Changelog

## [Unreleased] — English-first educational content and visual editing (pending review)

- Added a private, offline stage-level spaced review CLI with 1/3/7/14/30-day cadence, atomic gitignored local state, guarded updates, and 10 focused unit tests (issue #2).

- Built all 14 stage labs 00–13: onboarding, SQL, Python, batch ETL, PostgreSQL migrations/RLS, SCD2 warehouse modeling, dbt, orchestration, quality contracts, read-only Serving, release engineering, PySpark, Kafka, operations/recovery and integrated Capstone.
- Added independent learner starters, instructor references, adversarial graders, 14 Jupyter notebooks, a comprehensive teaching plan and prerequisite/exit-gate map.
- Added a 22-test end-to-end Capstone, reproducible artifact/rollback simulation, SQLite backup/restore and incident drills, evidence reviewer tools, exam rubrics and separately generated transfer-exam materials.
- The integrated 14-stage curriculum was verified on PR #15; later English-localization changes are reviewed in PR #16 with separate CI results.
- Converted the primary README, all 14 notebooks, remaining Hebrew learning guides, 11 stage modules, CS bridges, curriculum JSON and visible text in two dashboards to readable English; retained historical `.he.md` names to prevent broken links.
- Added VS Code extension recommendations (Jupyter/Python/Markdown), an optional installation helper, visual editor instructions and a CI guard that rejects Hebrew text in course assets.
- **External gates remain open**: independent learner pilot, human evaluation, optional owner-authorized Supabase cloud security/deployment, multi-node scaling claims, and professional accreditation.
- An instructor reference passing CI does not certify a learner or prove production readiness.

## [0.2.0] — 2026-11-04

- Expanded Hebrew README into start-to-end learner navigation, documented 10-step onboarding and milestones.
- Added original SVG hero/learning loop, Mermaid data flow and CS investigation diagrams.
- Added detailed Learner Handbook, Mastery Matrix, Project Ladder, Troubleshooting and Video Learning guides.
- Added four executable, offline-first Jupyter notebooks with original code, synthetic fixtures, optional YouTube players, fallback links and check questions.
- Expanded AI mentor guidance for adaptive pedagogy, teach-back, learning-debt logging, failure injection and video selection.
- Documented planned implementation backlog separately; no claim of cloud deployment or complete advanced module code.

## [0.1.0] — 2026-11-04

- Public self-paced Data Engineering roadmap (00–13), deliverables and competence gates.
- AI teaching prompt in Hebrew and English, CS bridges, side quests and adaptive learning protocol.
- Opt-in local hardware profiler; local-only learning progress CLI; test/CI validation.
- DataPulse educational starter, synthetic fixture, SQL schema, frontend demo and existing local tests.
- GitHub/MCP setup, explicit privacy/security/deployment safeguards.

**Historical note for v0.1.0:** advanced module implementation was incomplete at that release. See **Unreleased** above and the [current readiness ledger](docs/PROGRAM-READINESS.he.md) for the present educational coverage and independent release gates.
