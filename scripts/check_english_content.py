#!/usr/bin/env python3
"""Enforce English-first text in curriculum, notebooks, code and public UI.

This local-only check never modifies files, installs dependencies, runs notebook
cells or makes network requests. Historic '*.md' filenames are retained to
avoid breaking existing links; their *contents* must still be English.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HEBREW = re.compile(r"[\u0590-\u05FF]")
TEXT_SUFFIXES = frozenset({
    ".md", ".ipynb", ".json", ".py", ".sql", ".js", ".html", ".css",
    ".sh", ".ps1", ".yml", ".yaml", ".toml", ".svg", ".txt", ".example", ".csv", ".jsonl",
})
SKIP_PARTS = frozenset({
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    "target", "dist", "build", "dbt_packages", "logs",
})
EXTENSIONS = (
    "ms-python.python",
    "ms-toolsai.jupyter",
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced",
)
NOTEBOOK_COUNT = 14
# English canonical files co-exist with short legacy redirect pages.
CANONICAL_GUIDES = (
    "ADAPTIVE-LEARNING", "BREADTH-FOUNDATIONS",
    "COMPUTER-SCIENCE-BRIDGES", "ENVIRONMENT", "FINAL-ASSESSMENT",
    "FOUNDATIONS-LABS", "GITHUB-MCP-SETUP", "LEARNER-HANDBOOK",
    "MAINTAINER-ROADMAP", "MAINTAINERS", "MASTERY-MATRIX",
    "PROGRAM-READINESS", "PROJECT-LADDER", "PUBLISHING", "ROADMAP",
    "STAGE-04-SUPABASE-DEPLOY", "TEACHING-PLAN", "TROUBLESHOOTING",
    "VIDEO-LEARNING",
)
OTHER_CANONICAL_GUIDES = (
    "projects/datapulse/DEPLOYMENT-CHECKLIST",
    "projects/datapulse/LEARNING-PATH",
    "prompts/MASTER-AGENT",
)


def text_files(root: Path):
    """Yield tracked-style text assets; intentionally exclude generated data."""
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in (
            "README", "LICENSE", "AGENTS.md", "CHANGELOG.md",
            "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
        ):
            yield path


def scan_non_english(root: Path = ROOT) -> list[str]:
    """Find Hebrew code points without guessing a language from ASCII jargon."""
    failures = []
    for path in text_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            failures.append(f"{path.relative_to(root)}: cannot read UTF-8: {error}")
            continue
        match = HEBREW.search(content)
        if match is not None:
            line = content.count("\n", 0, match.start()) + 1
            failures.append(f"{path.relative_to(root)}:{line}: non-English Hebrew text found")
    return failures


def validate_visual_setup(root: Path = ROOT) -> list[str]:
    failures = []
    config_file = root / ".vscode" / "extensions.json"
    try:
        config = json.loads(config_file.read_text(encoding="utf-8"))
        recommended = config["recommendations"]
        if not isinstance(recommended, list) or set(EXTENSIONS) - set(recommended):
            failures.append("Missing required Markdown/Python/Jupyter extension recommendations")
    except (OSError, ValueError, KeyError, TypeError) as error:
        failures.append(f"Invalid VS Code extension recommendations: {error}")

    # Cross-platform installers are optional; verify their declared contents
    # without attempting local editor installation from CI.
    for installer in (
        root / "scripts" / "install-vscode-extensions.sh",
        root / "scripts" / "install-vscode-extensions.ps1",
    ):
        try:
            install_text = installer.read_text(encoding="utf-8")
            for extension in EXTENSIONS:
                if extension not in install_text:
                    failures.append(f"{installer.name}: missing extension {extension}")
        except OSError as error:
            failures.append(f"Missing or unreadable installer {installer.name}: {error}")

    required_setup_files = (
        "scripts/bootstrap-learning.sh",
        "scripts/bootstrap-learning.ps1",
        "scripts/verify_learning_environment.py",
        "notebooks/requirements-vscode.txt",
    )
    for name in required_setup_files:
        if not (root / name).is_file():
            failures.append(f"Missing real local setup asset: {name}")
    try:
        taskfile = json.loads((root / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
        tasklabels = {task.get("label") for task in taskfile["tasks"]}
        required = {
            "Course: Set up and verify this computer",
            "Course: Run local CI (no installations)",
            "Course: Full 14-notebook Jupyter integration",
        }
        if not required.issubset(tasklabels):
            failures.append("One-click setup/local CI VS Code tasks are missing")
    except (OSError, ValueError, KeyError, TypeError):
        failures.append("VS Code tasks.json cannot be read or parsed")

    guide = root / "docs" / "VS-CODE-LEARNING-SETUP.md"
    if not guide.is_file():
        failures.append("Missing visual-learning setup guide")

    for base in ("docs/" + item for item in CANONICAL_GUIDES):
        canonical = root / (base + ".md")
        legacy = root / (base + ".he.md")
        if not canonical.is_file() or canonical.stat().st_size < 400:
            failures.append(f"Missing or incomplete English guide: {canonical.relative_to(root)}")
        if not legacy.is_file():
            failures.append(f"Missing historical redirect: {legacy.relative_to(root)}")
        elif canonical.name not in legacy.read_text(encoding="utf-8"):
            failures.append(f"Historical guide does not point to canonical English file: {base}")
    for base in OTHER_CANONICAL_GUIDES:
        canonical = root / (base + ".md")
        legacy = root / (base + ".he.md")
        if not canonical.is_file() or canonical.stat().st_size < 400:
            failures.append(f"Missing or incomplete English guide: {canonical.relative_to(root)}")
        if not legacy.is_file():
            failures.append(f"Missing historical redirect: {legacy.relative_to(root)}")
        elif canonical.name not in legacy.read_text(encoding="utf-8"):
            failures.append(f"Historical guide does not point to canonical English file: {base}")

    notebooks = sorted((root / "notebooks").glob("*.ipynb"))
    if len(notebooks) != NOTEBOOK_COUNT:
        failures.append(f"Expected {NOTEBOOK_COUNT} guided notebooks; found {len(notebooks)}")
    for path in notebooks:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cells = data["cells"]
            if data.get("nbformat") != 4 or not isinstance(cells, list):
                raise ValueError("Notebook must use nbformat 4 and contain cells")
            if not cells or cells[0]["cell_type"] != "markdown":
                raise ValueError("Notebook must start with a rendered Markdown introduction")
            if not any(cell.get("cell_type") == "code" for cell in cells):
                raise ValueError("Notebook must contain at least one executable code cell")
            for cell in cells:
                if cell.get("cell_type") not in ("markdown", "code", "raw"):
                    raise ValueError("Unknown cell type")
                if not isinstance(cell.get("source"), (str, list)):
                    raise ValueError("Cell source must be text or a list of lines")
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures.append(f"{path.relative_to(root)}: invalid notebook: {error}")
    return failures


def validate(root: Path = ROOT) -> list[str]:
    return scan_non_english(root) + validate_visual_setup(root)


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("English-first asset validation failed:\n- " + "\n- ".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: English-only text assets, {NOTEBOOK_COUNT} Jupyter notebooks, "
          "four VS Code extension recommendations and setup guide")
