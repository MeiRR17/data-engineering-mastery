#!/usr/bin/env bash
# User-run first-time setup and local CI. Does not request cloud permissions.
# --verify-only: read-only checks, no extension/pip installs, no report writes.
# --all: execute all fourteen synthetic teaching notebooks using real ipykernel.
set -euo pipefail
mode="smoke"
verify_only=0
for arg in "$@"; do
  case "$arg" in
    --all) mode="all" ;;
    --verify-only) verify_only=1 ;;
    *) echo "Usage: bash scripts/bootstrap-learning.sh [--all] [--verify-only]" >&2; exit 2 ;;
  esac
done

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
if command -v python3 >/dev/null 2>&1; then
  system_python="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  system_python="$(command -v python)"
else
  echo "FAIL: install Python 3.11 or newer before course setup." >&2
  exit 2
fi

if [[ "$verify_only" -eq 0 ]]; then
  "$system_python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 2)'
  bash scripts/install-vscode-extensions.sh
  if [[ ! -x ".venv/bin/python" ]]; then
    "$system_python" -m venv .venv
  fi
  .venv/bin/python -m pip install --disable-pip-version-check \
    -r notebooks/requirements-vscode.txt
else
  bash scripts/install-vscode-extensions.sh --verify-only
  if [[ ! -x ".venv/bin/python" ]]; then
    echo "FAIL: missing .venv — use the setup task first." >&2
    exit 2
  fi
fi

echo "Checking VS Code, Markdown and Jupyter kernel (mode: $mode)"
if [[ "$verify_only" -eq 0 ]]; then
  .venv/bin/python scripts/verify_learning_environment.py --mode "$mode" --write-report
else
  .venv/bin/python scripts/verify_learning_environment.py --mode "$mode"
fi
echo "Running local learning CI tests"
.venv/bin/python scripts/validate_repo.py
.venv/bin/python scripts/audit_program.py
.venv/bin/python scripts/check_english_content.py
.venv/bin/python -m unittest discover -s tests -q
echo "PASS: local course setup and CI checks finished successfully."
if [[ "$verify_only" -eq 0 ]]; then
  echo "Sanitized results saved locally to learner/setup-check.local.json (gitignored)."
fi
