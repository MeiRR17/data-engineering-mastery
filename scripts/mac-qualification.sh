#!/usr/bin/env bash
# Opt-in, on-device qualification for the learner's current macOS VS Code environment.
# It MUST be launched on the Mac itself; a GitHub-hosted macOS runner is different.
# Does not request admin access, change global Python or upload private data.
set -euo pipefail
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "FAIL: this task must run directly on a macOS computer." >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

if ! command -v git >/dev/null 2>&1 || ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FAIL: open a Git checkout of the course in VS Code before qualification." >&2
  exit 2
fi

# A true local CI: extension install + Python venv + repo tests + 14 live kernels.
bash scripts/bootstrap-learning.sh --all

# All gates must have passed before this stage. Check the report and commit.
.venv/bin/python - <<'PY'
import json
import platform
from pathlib import Path
import subprocess

report = json.loads(Path("learner/setup-check.local.json").read_text(encoding="utf-8"))
assert platform.system() == "Darwin", "not running on macOS"
assert report["status"] == "PASS", report["issues"]
assert report["execution_scope"] == "THIS_CLI_CONTEXT_ONLY"
assert report["markdown_parsed_to_html"] is True
assert len(report["installed_extensions"]) == 4, "four actual VS Code extensions are required"
assert len(report["executed_notebooks"]) == 14, "all fourteen notebooks must execute"
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
assert len(head) == 40
print("LOCAL_MAC_COURSE_CI=PASS")
print("GIT_COMMIT=" + head)
print("VSCODE_EXTENSIONS_VERIFIED=" + str(len(report["installed_extensions"])))
print("JUPYTER_NOTEBOOKS_EXECUTED=" + str(len(report["executed_notebooks"])))
print("LOCAL_EVIDENCE=learner/setup-check.local.json")
print("VISUAL_EDITOR_ACTIVATION=NOT_VERIFIED_BY_CLI")
PY

# Present a formatted lesson and a live notebook automatically for visual confirmation.
if command -v code >/dev/null 2>&1; then
  code --reuse-window docs/QUICKSTART.en.md notebooks/00_data_journey.ipynb || true
elif [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
  "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" --reuse-window \
    docs/QUICKSTART.en.md notebooks/00_data_journey.ipynb || true
fi

echo "PASS: verified on THIS Mac. Inspect the opened Markdown preview and notebook cells visually."
