# Data Engineering Mastery

A public, forkable, **project-first** path from software engineering graduate to production-oriented data engineering. Start with SQL, Python and batch ETL; continue through Supabase/PostgreSQL, modeling, orchestration, quality, cloud, Spark, Kafka and a capstone. Each stage has tasks, acceptance criteria, a practical deliverable and a review gate.

**Start here:** [Hebrew README](README.md) · [English quickstart](docs/QUICKSTART.en.md) · [Full roadmap](docs/ROADMAP.he.md) · [Mentor prompt (English)](prompts/MASTER-AGENT.en.md)

Run without accounts or cloud costs:

```bash
python3 scripts/roadmap.py init --alias learner
python3 scripts/roadmap.py status
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
PYTHONPATH=projects/datapulse/src python3 -m datapulse.ingest --fixture projects/datapulse/data/sample.geojson --dry-run
```

Cloud deployments are separate, opt-in, and may cost money. The starter is **not already deployed**; its example dataset is synthetic. Always verify secrets and access permissions before making any endpoint public.

For a personal journey, create a repository from the template on your own GitHub account, then connect your own ChatGPT GitHub plugin and/or the official GitHub MCP Server to a supported IDE. Authentication is **never performed by copying credentials into prompts**.

License: MIT. PRs improving accessibility, translations and exercises are welcome.

## Guided learning, notebooks, videos

For the complete step-by-step onboarding and troubleshooting guide (currently in Hebrew), see [Learner Handbook](docs/LEARNER-HANDBOOK.he.md), [Notebook + YouTube guide](docs/VIDEO-LEARNING.he.md), [Mastery Matrix](docs/MASTERY-MATRIX.he.md), and [Notebooks](notebooks/README.md). The repository contains four runnable offline notebooks; videos remain on their original platforms. This is learning infrastructure, not verified cloud deployment or a certificate.

## Complete 14-stage curriculum implementation

The integrated curriculum now includes code labs for stages 00–12, an end-to-end Stage 13 capstone, 14 guided notebooks, independent transfer-exam variants, a five-dimension rubric and an evidence structure validator. CI exercises instructor references including isolated PostgreSQL/dbt, local PySpark and a disposable single-node Kafka broker. This does **not** certify any individual learner, verify multi-node performance, or prove production/cloud readiness. Read [the readiness ledger](docs/PROGRAM-READINESS.he.md) and [the complete learner plan](docs/TEACHING-PLAN.he.md). No external credential or cloud deployment was issued; main integration does not establish learner proficiency.
