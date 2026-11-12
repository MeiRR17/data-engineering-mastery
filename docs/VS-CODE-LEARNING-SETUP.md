# Visual Studio Code: readable Markdown and interactive notebooks

This repository uses **English-language Markdown (`.md`) lessons** and **Jupyter (`.ipynb`) notebooks**. VS Code can present both in a visual editor; you should not have to inspect notebook JSON or raw Markdown.

## Recommended extensions

| Extension | Official identifier | Why to install it |
| --- | --- | --- |
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | `ms-python.python` | Python environments, debugging and interpreter selection |
| [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) | `ms-toolsai.jupyter` | Visual notebook cells, code execution, plots and kernel selection |
| [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one) | `yzhang.markdown-all-in-one` | Editing shortcuts, headings and table of contents |
| [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced) | `shd101wyy.markdown-preview-enhanced` | Rich preview, Mermaid diagrams, math and export options |

The [workspace recommendations](../.vscode/extensions.json) appear when opening this project folder. A repository **cannot silently install** extensions on your computer; installation is always your choice.

To install all four on **macOS/Linux/WSL** from the repository root:

~~~bash
bash scripts/install-vscode-extensions.sh
~~~

For **Windows PowerShell**, run this from the repository root:

~~~powershell
powershell -NoProfile -File .\scripts\install-vscode-extensions.ps1
~~~

The Windows helper verifies that the four extensions appear in VS Code's installed list. If PowerShell's execution policy blocks scripts, use the four manual `code --install-extension` commands below or install through **Extensions (Ctrl+Shift+X)**. Do not change a machine-wide execution policy to follow a lesson.

Or install manually on macOS, Linux or Windows when VS Code's `code` CLI is available:

~~~bash
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension yzhang.markdown-all-in-one
code --install-extension shd101wyy.markdown-preview-enhanced
~~~

**macOS:** if `code` is not found, open VS Code, press Cmd+Shift+P and select **Shell Command: Install 'code' command in PATH**, then open a new terminal.

## Install from inside VS Code (no commands to copy)

Open the project folder, then choose **Terminal → Run Task** and select **Course: Install VS Code Markdown and Jupyter extensions**. This is a user-triggered task: it runs the included PowerShell installer on Windows, or the Bash installer on macOS/Linux. You can also choose **Course: Validate English lessons and notebooks** to check the files without installing anything. If your system blocks scripts, install the four extensions manually through the VS Code Extensions sidebar; do not change system-wide security policy just for this course.

## Full local macOS qualification (one task)

**This is the actual learner-Mac test, not GitHub's disposable macOS CI runner.**
Open the current project checkout in the local VS Code app, then choose:
**Terminal → Run Task → Course: Qualify this Mac (full local CI)**.

The task runs `bash scripts/mac-qualification.sh` locally. It installs and verifies
all four VS Code Marketplace extensions in the active CLI context, creates the
isolated Python environment, validates the curriculum, runs repository tests,
executes **all fourteen real Jupyter notebooks**, and checks the resulting
gitignored `learner/setup-check.local.json` is PASS. It prints
`LOCAL_MAC_COURSE_CI=PASS` and the tested Git commit only after every gate
passes. Failures return nonzero, never a success banner.

To run the identical on-Mac qualification from Terminal, use
`bash scripts/mac-qualification.sh` from the root of the repository.
The script opens a Markdown lesson and a Jupyter notebook in VS Code for
immediate visual confirmation. It does **not** claim that a CLI check can certify
graphical preview activation, every VS Code profile, or the device's identity.
Nothing is uploaded automatically; the sanitized local report stays gitignored.

Before using this Mac task, make sure you are in the **qualification branch** that
contains it, not an older version of `main`. Do not run scripts directly from
unreviewed websites and do not install a public pull-request self-hosted runner
on a personal computer.

## Real computer setup and local CI (recommended)

**One action inside VS Code:** Open the whole repository folder, select **Terminal → Run Task → Course: Set up and verify this computer**. It requests no cloud account and performs actual setup on the machine/context running the task:

1. Install or refresh the four extensions from VS Code Marketplace and query `code --list-extensions --show-versions` to confirm their **actual installed IDs and versions**. Merely listing them in `.vscode/extensions.json` is no longer considered success.
2. Create a gitignored, isolated `.venv` and install the pinned [lightweight notebook dependencies](../notebooks/requirements-vscode.txt), including `ipykernel`, `nbclient` and Matplotlib. Nothing is installed system-wide by the Python step.
3. Parse the course Markdown to HTML and **execute three real notebooks** (Stages 00, 04 and 13) using the Jupyter Python kernel, including real code outputs and errors.
4. Run the curriculum audit and local unit tests. Every failed command stops the setup; it will not print a false PASS.
5. Save a sanitized, **local-only** `learner/setup-check.local.json` with package and extension versions, notebook names and PASS/FAIL status. The file is gitignored and excludes username, host, home paths, tokens and source data.

For an installation that you only need to check again, choose **Terminal → Run Task → Course: Run local CI (no installations)**. This verifies installed extensions and dependencies and executes real notebook cells **without writing a report or installing anything**.

To execute every one of the 14 notebooks, choose **Terminal → Run Task → Course: Full 14-notebook Jupyter integration**. It uses the same environment and does not require a network connection to execute synthetic cells.

**Windows and macOS:** the tasks automatically select PowerShell on Windows and Bash on macOS/Linux. The Windows task uses process-scoped `RemoteSigned` to run the repository's reviewed local script; this does not change system-wide PowerShell policy. If your organization enforces stricter policy, use the manual installation instructions and ask the administrator rather than overriding policy.

### What the real CI verifies

The GitHub workflow launches **disposable Ubuntu, Apple Silicon macOS and Windows runners**, downloads VS Code from Microsoft's official download endpoint, installs all four Marketplace extensions, creates a Python environment and executes **all 14 notebooks using real Jupyter kernels**. This detects broken extensions, missing kernels, incompatible dependencies and failing cell execution rather than merely inspecting JSON files.

An automated CLI cannot prove that the editor's graphical tab is visible in your **personal** VS Code session or that an extension is enabled in every profile. After the local task passes, open one `.md` using Markdown Preview and one `.ipynb` in Jupyter Notebook view. This manual UI check complements, but does not replace, the automated checks.

For WSL or SSH Remote environments, extension installation and kernel checks apply to the context in which the task is running. If you want a Windows-host editor profile instead of the WSL extension host, run the task from a Windows-local VS Code window.


## Read Markdown as a formatted page

1. Use **File → Open Folder** to open the whole repository.
2. Open [README.md](../README.md).
3. Press **Cmd+Shift+V** (Mac) or **Ctrl+Shift+V** (Windows/Linux) for the built-in Markdown preview.
4. For editing and preview side by side: **Cmd+K, V** (Mac) / **Ctrl+K, V** (Windows/Linux).
5. For more advanced visual rendering, run **Markdown Preview Enhanced: Open Preview to the Side** from the Command Palette. Fenced `mermaid` blocks render as diagrams.

## Open Jupyter notebooks visually

1. Install Python and the Jupyter extension.
2. Open [notebooks/00_data_journey.ipynb](../notebooks/00_data_journey.ipynb) in Explorer.
3. The editor should show **Markdown and Code cells**, not raw JSON. If it shows JSON: right-click the tab → **Reopen Editor With... → Jupyter Notebook**.
4. Select the correct Python kernel at the top right and run one cell at a time.
5. If no kernel is available, create a virtual environment (macOS/Linux):

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade ipykernel
~~~

On Windows, activate the virtual environment using the Windows-specific command. Some earlier notebooks also use packages from [notebooks/requirements.txt](../notebooks/requirements.txt). You do **not** need to install Spark or Kafka just to read notebook pages.

## A useful learning layout

Use Explorer and Outline on the left, a **rendered Markdown lesson** in the center, and a **notebook or terminal** on the right. Predict the result before executing a cell. Then complete the student lab, run its test suite and explain the failure mode in English.

## Troubleshooting

| Problem | Action |
| --- | --- |
| `.md` looks like code | Press Cmd/Ctrl+Shift+V or run **Markdown: Open Preview** |
| `.ipynb` opens as raw JSON | **Reopen Editor With... → Jupyter Notebook** |
| No notebook kernel | Select a Python interpreter and install `ipykernel` in it |
| Mermaid shows source text | Use Markdown Preview Enhanced and a fenced `mermaid` block |
| `code` command missing | Enable the VS Code CLI or install in the Extensions sidebar |
| Missing Python package | Choose the right environment and install only documented dependencies |

**Security:** VS Code extensions are installed on your computer and run third-party code. Review their publishers and permissions. Do not run executable chunks from untrusted Markdown or place credentials, private records, or reviewer-only answers in notebooks.
