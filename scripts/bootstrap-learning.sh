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
# Prefer an actually supported interpreter, not macOS' first (possibly old) python3.
# No system-wide Python installation or sudo is performed.
system_python=""
if [[ "$verify_only" -eq 0 ]]; then
  candidates=()
  if [[ -n "${COURSE_PYTHON:-}" ]]; then
    candidates+=("$COURSE_PYTHON")
  fi
  candidates+=(python3.12 python3.13 python3.14 python3.11 python3 python)
  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1 && \
       "$candidate" -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info < (3, 15) else 2)' >/dev/null 2>&1; then
      system_python="$candidate"
      break
    fi
  done
  if [[ -z "$system_python" ]]; then
    echo "FAIL: Python 3.11–3.14 is required. Install it and rerun this task." >&2
    exit 2
  fi
  # Clear a prior success so it cannot be mistaken for this setup run.
  rm -f -- learner/setup-check.local.json
fi

if [[ "$verify_only" -eq 0 ]]; then
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

echo "Running local learning CI tests"
.venv/bin/python scripts/validate_repo.py
.venv/bin/python scripts/audit_program.py
.venv/bin/python scripts/check_english_content.py
.venv/bin/python -m unittest discover -s tests -q
# The PASS report is written only after every other local CI gate passed.
echo "Checking VS Code, Markdown and Jupyter kernel (mode: $mode)"
if [[ "$verify_only" -eq 0 ]]; then
  .venv/bin/python scripts/verify_learning_environment.py --mode "$mode" --write-report
else
  .venv/bin/python scripts/verify_learning_environment.py --mode "$mode"
fi
echo "PASS: local course setup and CI checks finished successfully."
if [[ "$verify_only" -eq 0 ]]; then
  echo "Sanitized results saved locally to learner/setup-check.local.json (gitignored)."
fi
