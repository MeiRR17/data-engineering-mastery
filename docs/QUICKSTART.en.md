# Quickstart — zero account, zero cloud cost

1. Use GitHub's **Use this template** for your own learning repository, or download and unpack the source.
2. Install Python 3.11+, Git and an editor. Cloud and Docker are **optional** for Stage 00.
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
5. Every module leads to a branch, tests, a reflection and an assessment gate. Completion records are local-only and self-reported until independently reviewed.
6. Follow [GitHub/MCP guide](GITHUB-MCP-SETUP.he.md), [resource policy](ENVIRONMENT.he.md), [roadmap](ROADMAP.he.md), and [assessment rubric](ASSESSMENT.md).

Never share tokens, service keys, raw system inventories or personal data in public repositories. New Supabase projects can cost money; deployment is opt-in.
