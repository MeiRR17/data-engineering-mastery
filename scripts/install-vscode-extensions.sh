#!/usr/bin/env bash
# Optional, user-initiated VS Code extension installation (macOS/Linux/WSL).
# The repo does not install extensions automatically or change user settings.
set -euo pipefail
if ! command -v code >/dev/null 2>&1; then
  cat >&2 <<'INFO'
VS Code's 'code' command is not available in this shell.
On macOS: open VS Code, press Cmd+Shift+P, then run:
  Shell Command: Install 'code' command in PATH
On Windows: use VS Code's Extensions view or a terminal where 'code' works.
You can also install from Extensions (Cmd/Ctrl+Shift+X) by searching each ID.
INFO
  exit 2
fi
for extension in \
    ms-python.python \
    ms-toolsai.jupyter \
    yzhang.markdown-all-in-one \
    shd101wyy.markdown-preview-enhanced
do
  echo "Installing VS Code extension: $extension"
  code --install-extension "$extension"
done
printf '\nExtension installation commands completed.\n'
printf 'Open this project as a VS Code folder and select a Python kernel for .ipynb files.\n'
