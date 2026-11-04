#!/usr/bin/env bash
# Maintainer tool for an EXISTING repository. Never force-pushes, merges or changes main.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
repo="${1:-MeiRR17/data-engineering-mastery}"
if [[ ! "$repo" =~ ^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$ ]]; then
  echo 'Expected owner/repository' >&2; exit 2
fi
for cmd in gh git rsync python3; do
  command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }
done
gh auth status >/dev/null 2>&1 || { echo 'Run gh auth login' >&2; exit 2; }
python3 "$root/scripts/validate_repo.py"
(cd "$root" && python3 -m unittest discover -s tests -q)
(cd "$root" && PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -q)
work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT
gh repo clone "$repo" "$work/repo" -- --depth=1
branch="maintenance/learning-kit-$(date -u +%Y%m%d-%H%M%S)"
git -C "$work/repo" switch -c "$branch"
# Never --delete remote content. Never copy local credentials or progress.
rsync -a \
  --exclude='/.git/' --exclude='.venv/' --exclude='__pycache__/' \
  --exclude='.ipynb_checkpoints/' --exclude='*.pyc' --exclude='.DS_Store' \
  --include='.env.example' --exclude='.env' --exclude='.env.*' \
  --exclude='*.pem' --exclude='*.key' --exclude='*.p12' \
  --exclude='learner/progress.json' --exclude='learner/system-profile.local.json' \
  --exclude='*.sqlite3' --exclude='*.db' \
  "$root/" "$work/repo/"
git -C "$work/repo" add -A
unsafe=0
while IFS= read -r changed; do
  base="$(basename "$changed")"
  case "$base" in
    .env|.env.*) [[ "$base" == '.env.example' ]] || unsafe=1 ;;
    progress.json|system-profile.local.json|id_rsa|*.pem|*.key|*.p12) unsafe=1 ;;
  esac
done < <(git -C "$work/repo" diff --cached --name-only)
if [[ "$unsafe" -ne 0 ]]; then
  echo 'Potential secret staged. No remote changes made.' >&2; exit 3
fi
if git -C "$work/repo" diff --cached --quiet; then echo 'No changes to publish.'; exit 0; fi
git -C "$work/repo" diff --cached --stat
printf 'Type CREATE-PR to publish a reviewable branch: '
read -r answer
[[ "$answer" == CREATE-PR ]] || { echo 'Cancelled.'; exit 0; }
git -C "$work/repo" commit -m 'chore: propose reviewed learning-kit updates'
git -C "$work/repo" push -u origin "$branch"
gh pr create --repo "$repo" --base main --head "$branch" \
  --title 'chore: update Data Engineering learning kit' \
  --body 'Validated locally; please review all changes before merging.'
