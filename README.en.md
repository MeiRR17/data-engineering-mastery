# Data Engineering Mastery — English entry point

The full course documentation now lives in the **[English-first README](README.md)**. This compatibility entry point remains so existing links to `README.en.md` continue working.

**Start visually:** [VS Code Markdown and Jupyter setup](docs/VS-CODE-LEARNING-SETUP.md) · [English quickstart](docs/QUICKSTART.en.md) · [14-stage course roadmap](docs/ROADMAP.he.md) · [Interactive notebooks](notebooks/README.md)

The program contains a synthetic DataPulse capstone, 14 stages, independently graded student exercises, maintainer reference solutions and an examination framework. **Passing instructor CI does not certify learners or establish cloud production readiness.**

~~~bash
# In macOS/Linux/WSL with the VS Code CLI installed:
bash scripts/install-vscode-extensions.sh

# Test the course structure and English content:
python3 scripts/validate_repo.py
python3 scripts/check_english_content.py
python3 -m unittest discover -s tests -v
~~~

On Windows use `powershell -NoProfile -File .\scripts\install-vscode-extensions.ps1` from the repository root. The VS Code extension scripts are opt-in: it installs **Python**, **Jupyter**, **Markdown All in One** and **Markdown Preview Enhanced** on your computer if you choose to run it. Opening `.md` files in Markdown Preview or `.ipynb` files in the Jupyter Notebook editor makes the lessons visual, with formatted text, diagrams, executable cells and plots.

[Assessment](docs/FINAL-ASSESSMENT.he.md) · [Safe GitHub setup](docs/GITHUB-MCP-SETUP.he.md) · [Security policy](SECURITY.md).
