# Publishing and maintaining a public course repository

> **Current status:** The Data Engineering Mastery source repository already exists on GitHub. These instructions describe **creating another copy**, not a claim that a remote repository has not yet been created. Publishing or pushing to a new owner account requires that owner's explicit approval.

## Option A — user-initiated first-time publishing script

On a Mac with Homebrew:

~~~bash
brew install gh git
gh auth login
~~~

Authenticate through the GitHub browser/device flow. Do not share account passwords or PATs in chat. From the local repository root:

~~~bash
python3 scripts/validate_repo.py
python3 scripts/audit_program.py
python3 -m unittest discover -s tests -v
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
bash scripts/publish_to_github.sh
~~~

Review the script **before** running it. It checks the GitHub account, shows the files it would publish and requires confirmation; it must not force-push over an existing repository.

## Option B — GitHub website and manual Git

1. Open [GitHub's new repository page](https://github.com/new) under the intended account.
2. Choose a repository name and appropriate public/private visibility. Do not add duplicate README or ignore files when importing an existing Git tree.
3. If starting from a local directory with no Git history, use:

~~~bash
git init -b main
git add .
git commit -m "feat: publish learning course"
git remote add origin https://github.com/YOUR_ACCOUNT/data-engineering-mastery.git
git push -u origin main
~~~

If the folder already has history, **do not blindly reinitialize it**; inspect `git status` and `git remote -v` first.

4. Confirm that README renders visually and the GitHub Actions learning checks pass.
5. Enable **Template repository**, PR review and branch protection/rulesets as appropriate for the account plan.
6. Create a semantic release tag only when all applicable gates are satisfied and the changelog is accurate.
7. Share the source URL with the learner. They should create a **learner-owned copy**, not commit personal progress into upstream.

## Onboard a new learner

- Install Python, Git and VS Code with the recommended [Markdown and Jupyter extensions](VS-CODE-LEARNING-SETUP.md).
- Optionally classify hardware with `python3 scripts/system_profile.py --tier-only`.
- Initialize local/private progress using `python3 scripts/roadmap.py init --alias learner` and view the next task.
- Connect GitHub to ChatGPT or an IDE agent **only when useful and with explicit permissions**; see [GitHub setup](GITHUB-MCP-SETUP.he.md).
- Use the [English mentor prompt](../prompts/MASTER-AGENT.en.md), start Stage 00 and work through branch → PR → tests → evidence → review.

## Public maintenance

Use meaningful semantic releases and a clear CHANGELOG. Gather feedback via Issues/Discussions without exposing learner assessment data or full machine profiles. Encourage original corrections to tests, datasets, English docs and OS support. Neither the template nor a single exercise outcome should be described as an externally accredited professional certificate.
