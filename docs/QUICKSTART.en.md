# Quickstart — zero account, zero cloud cost

1. Use GitHub's **Use this template** for your own learning repository, or download and unpack the source.
2. Install Python 3.11+, Git and VS Code. Then open **Terminal → Run Task → Course: Set up and verify this computer**. This installs four real editor extensions, creates a private `.venv`, launches actual Jupyter kernels and runs local repository tests. [Setup guide](VS-CODE-LEARNING-SETUP.md). Cloud and Docker are optional for Stage 00.
3. From the root run:

```bash
python3 scripts/system_profile.py
python3 scripts/roadmap.py init --alias learner
python3 scripts/roadmap.py status
python3 scripts/roadmap.py next
python3 scripts/validate_repo.py
python3 -m unittest discover -s projects/datapulse/tests -v
```

4. Open `curriculum/modules/00.md` and paste `prompts/MASTER-AGENT.en.md` into an AI tutor, or allow it to read through a separately authorized GitHub integration.
5. Optionally schedule local, private spaced reviews of weak topics using [the spaced-review guide](SPACED-REVIEW.md); reviews are not an assessment.
6. Every module leads to a branch, tests, a reflection and an assessment gate. Completion records are local-only and self-reported until independently reviewed.
7. Follow [GitHub/MCP guide](GITHUB-MCP-SETUP.md), [resource policy](ENVIRONMENT.md), [roadmap](ROADMAP.md), and [assessment rubric](ASSESSMENT.md).

Never share tokens, service keys, raw system inventories or personal data in public repositories. New Supabase projects can cost money; deployment is opt-in.
