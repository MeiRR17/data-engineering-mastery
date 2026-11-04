#!/usr/bin/env bash
# Deliberately interactive, non-destructive publication; run from the repository root.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v git >/dev/null; then echo 'Install Git first.' >&2; exit 1; fi
if ! command -v gh >/dev/null; then echo 'Install GitHub CLI: https://cli.github.com/ (on macOS: brew install gh).' >&2; exit 1; fi
if ! gh auth status >/dev/null 2>&1; then echo 'Authenticate first with: gh auth login' >&2; exit 1; fi
if [[ -e .git ]]; then echo 'Git repo already exists; use normal Git workflow, not this first-publish helper.' >&2; exit 1; fi
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -q
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -q
read -r -p 'GitHub owner login for the new PUBLIC repository: ' owner
if [[ ! "$owner" =~ ^[A-Za-z0-9-]+$ ]]; then echo 'Invalid owner.' >&2; exit 1; fi
repo="${owner}/data-engineering-mastery"
if gh repo view "$repo" >/dev/null 2>&1; then
  echo "Repository $repo already exists; refusing to overwrite." >&2
  exit 1
fi
echo "Will create GitHub PUBLIC repo: $repo"
echo 'This publishes all tracked teaching files and makes them accessible to anyone.'
echo 'Private learner progress, system profile and .env files are excluded by .gitignore.'
read -r -p 'Type PUBLIC to confirm, anything else aborts: ' decision
if [[ "$decision" != 'PUBLIC' ]]; then echo 'Cancelled.'; exit 1; fi
git init -b main
git add .
if git diff --cached --name-only | grep -E '(^|/)(\.env([^/]*|$)|progress\.json|system-profile\.local\.json|id_rsa|.*\.pem)$' ; then
  echo 'Potential secret or local private file staged. Aborting publication.' >&2
  exit 1
fi
echo 'Staged files:'
git diff --cached --stat
git commit -m 'feat: publish Data Engineering Mastery v0.2.0 learning kit'
gh repo create "$repo" --public --source . --remote origin --push --description 'Adaptive, project-based Data Engineering roadmap from CS foundations to production'
echo "Published: https://github.com/$repo"
echo 'Next: Settings > General > Template repository; then protect main and check Actions.'
