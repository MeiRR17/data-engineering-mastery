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

Or install manually on macOS, Linux or Windows when VS Code's `code` CLI is available:

~~~bash
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension yzhang.markdown-all-in-one
code --install-extension shd101wyy.markdown-preview-enhanced
~~~

**macOS:** if `code` is not found, open VS Code, press Cmd+Shift+P and select **Shell Command: Install 'code' command in PATH**, then open a new terminal.

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
