#!/usr/bin/env bash
# Install/verify extensions in the CURRENT VS Code CLI context, only on request.
# Optional --verify-only makes no changes. Never uses sudo or remote credentials.
set -euo pipefail

readonly required=(
  ms-python.python
  ms-toolsai.jupyter
  yzhang.markdown-all-in-one
  shd101wyy.markdown-preview-enhanced
)

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--verify-only" ) ]]; then
  echo "Usage: bash scripts/install-vscode-extensions.sh [--verify-only]" >&2
  exit 2
fi
verify_only=0
[[ "${1:-}" == "--verify-only" ]] && verify_only=1

if [[ -n "${VSCODE_CLI:-}" ]]; then
  code_cli="$VSCODE_CLI"
elif command -v code >/dev/null 2>&1; then
  code_cli="$(command -v code)"
elif [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
  code_cli="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
elif [[ -x "$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
  code_cli="$HOME/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
else
  echo "FAIL: VS Code CLI not available in this terminal." >&2
  echo "macOS: Open VS Code -> Command Palette -> Shell Command: Install 'code' command in PATH." >&2
  echo "Windows: use the PowerShell installer from Windows (not from WSL) for Windows extensions." >&2
  exit 2
fi

if ! "$code_cli" --version >/dev/null 2>&1; then
  echo "FAIL: VS Code CLI is not functioning." >&2
  exit 2
fi

if [[ $verify_only -eq 0 ]]; then
  for extension in "${required[@]}"; do
    echo "Installing/refreshing extension: $extension"
    "$code_cli" --install-extension "$extension"
  done
fi

# Listing the ACTUAL current profile is stronger than inspecting extensions.json.
installed="$("$code_cli" --list-extensions --show-versions | tr '[:upper:]' '[:lower:]')"
failed=0
for extension in "${required[@]}"; do
  if printf '%s\n' "$installed" | grep -Eq "^${extension//./\\.}@[0-9]+"; then
    echo "PASS: installed $extension"
  else
    echo "FAIL: missing installed extension $extension" >&2
    failed=1
  fi
done
if [[ $failed -ne 0 ]]; then
  echo "Open VS Code's Extensions view and check your current local/remote profile." >&2
  exit 1
fi
echo "PASS: all four VS Code extensions are installed in the CLI context checked."
