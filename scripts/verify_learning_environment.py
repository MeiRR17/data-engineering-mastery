#!/usr/bin/env python3
"""Prove the *current machine's* VS Code/Jupyter prerequisites really work.

An isolated GitHub runner can run the same check, but its result does NOT prove
extensions were installed on a learner's personal Mac/Windows computer.

The report contains only dependency versions and PASS/FAIL; no hostname,
username, home path, environment variables, file contents or credentials.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EXTENSIONS = (
    "ms-python.python",
    "ms-toolsai.jupyter",
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced",
)
RUNTIME_PACKAGES = ("ipykernel", "nbclient", "nbformat", "matplotlib", "markdown-it-py")
SMOKE_NOTEBOOKS = (
    "00_data_journey.ipynb",
    "04_postgres_security.ipynb",
    "13_integrated_capstone.ipynb",
)
REPORT = ROOT / "learner" / "setup-check.local.json"


def parse_extensions(output: str) -> dict[str, str]:
    """VS Code --list-extensions --show-versions, ignoring unrelated output."""
    matches = {}
    for line in output.splitlines():
        m = re.fullmatch(r"([a-zA-Z0-9_-]+\.[a-zA-Z0-9_.-]+)@([0-9][^\s]*)",
                         line.strip())
        if m:
            matches[m.group(1).lower()] = m.group(2)
    return matches


def find_code_cli() -> str | None:
    override = os.environ.get("VSCODE_CLI")
    if override:
        return override
    found = shutil.which("code")
    if found:
        return found
    for path in (
        Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
        Path.home() / "Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
    ):
        if path.is_file():
            return str(path)
    return None


def check_extensions() -> tuple[dict[str, str], list[str]]:
    cli = find_code_cli()
    if not cli:
        return {}, ["VSCODE_CLI_MISSING"]
    try:
        response = subprocess.run(
            [cli, "--list-extensions", "--show-versions"],
            check=False, capture_output=True, text=True, timeout=70,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}, ["VSCODE_CLI_UNAVAILABLE"]
    if response.returncode != 0:
        return {}, ["VSCODE_EXTENSION_QUERY_FAILED"]
    installed = parse_extensions(response.stdout)
    failures = [f"EXTENSION_MISSING:{name}" for name in REQUIRED_EXTENSIONS
                if name not in installed]
    return ({name: installed[name] for name in REQUIRED_EXTENSIONS if name in installed},
            failures)


def check_packages() -> tuple[dict[str, str], list[str]]:
    found, missing = {}, []
    for name in RUNTIME_PACKAGES:
        try:
            found[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(f"PACKAGE_MISSING:{name}")
    return found, missing


def check_markdown_render() -> bool:
    """Actual Markdown parsing to HTML; not a graphical VS Code activation test."""
    from markdown_it import MarkdownIt
    parser = MarkdownIt("commonmark").enable("table")
    home = parser.render((ROOT / "README.md").read_text(encoding="utf-8"))
    capstone = parser.render((ROOT / "capstone" / "README.md").read_text(encoding="utf-8"))
    return "<h1>" in home and "<table>" in home and "language-mermaid" in capstone


def execute_notebooks(mode: str) -> tuple[list[str], list[str]]:
    if mode == "none":
        return [], []
    import nbformat
    from nbclient import NotebookClient

    # Never edit source notebooks. No network needed; data is synthetic.
    os.environ.setdefault("MPLBACKEND", "Agg")
    paths = ([ROOT / "notebooks" / n for n in SMOKE_NOTEBOOKS]
             if mode == "smoke" else sorted((ROOT / "notebooks").glob("*.ipynb")))
    completed = []
    issues = []
    for path in paths:
        try:
            nb = nbformat.read(str(path), as_version=4)
            nbformat.validate(nb)
            client = NotebookClient(
                nb, timeout=75, startup_timeout=50, kernel_name="python3",
                allow_errors=False,
                resources={"metadata": {"path": str(ROOT)}},
            )
            executed = client.execute()
            errors = [out for cell in executed.cells if cell.cell_type == "code"
                      for out in cell.get("outputs", []) if out.output_type == "error"]
            if errors:
                raise RuntimeError("Notebook code cell returned an error output")
        except Exception as error:
            # Public CI runs only our allowlisted synthetic source notebooks.
            # Print a bounded tail of the real cell exception for debugging,
            # never write the exception into the private local readiness report.
            if os.environ.get("GITHUB_ACTIONS") == "true":
                detail = str(error)
                print(f"CI_NOTEBOOK_DIAGNOSTIC:{path.name}:"
                      f"{type(error).__name__}:"
                      + detail[-1700:], file=sys.stderr, flush=True)
            issues.append(f"NOTEBOOK_FAILED:{path.name}:{type(error).__name__}")
        else:
            completed.append(path.name)
            print(f"PASS: real Jupyter kernel executed {path.name}", flush=True)
    return completed, issues


def verify(mode: str = "smoke") -> dict:
    problems = []
    if sys.version_info < (3, 11):
        problems.append("PYTHON_TOO_OLD")
    if sys.version_info >= (3, 15):
        problems.append("PYTHON_VERSION_NOT_VALIDATED")
    extensions, e_issues = check_extensions()
    problems.extend(e_issues)
    packages, p_issues = check_packages()
    problems.extend(p_issues)
    rendered = False
    notebooks = []
    if not p_issues and (3, 11) <= sys.version_info < (3, 15):
        try:
            rendered = check_markdown_render()
            if not rendered:
                problems.append("MARKDOWN_RENDER_FAILED")
        except (ImportError, OSError, ValueError):
            problems.append("MARKDOWN_RENDER_UNAVAILABLE")
        notebooks, n_issues = execute_notebooks(mode)
        problems.extend(n_issues)
    else:
        problems.append("RUNTIME_NOT_READY")
    return {
        "schema_version": 1,
        "status": "PASS" if not problems else "FAIL",
        "execution_scope": "THIS_CLI_CONTEXT_ONLY",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "installed_extensions": extensions,
        "installed_packages": packages,
        "markdown_parsed_to_html": rendered,
        "executed_notebooks": notebooks,
        "notebook_mode": mode,
        "issues": problems,
        "not_verified": [
            "graphical VS Code editor activation",
            "editor extension enabled state",
            "a different machine, VS Code profile or Remote/WSL context",
            "learner competency or cloud deployment",
        ],
    }


def write_local_report(report: dict) -> None:
    if REPORT.is_symlink():
        raise RuntimeError("Refusing to overwrite symlinked local report")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "all", "none"), default="smoke")
    parser.add_argument("--write-report", action="store_true",
                        help="Write sanitized, gitignored learner/setup-check.local.json")
    args = parser.parse_args()
    results = verify(args.mode)
    if args.write_report:
        write_local_report(results)
    print(json.dumps(results, sort_keys=True, indent=2))
    return 0 if results["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
