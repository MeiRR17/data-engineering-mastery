#!/usr/bin/env python3
"""Validate public curriculum structure and local repo links. No network requests."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    errors = []
    try:
        data = json.loads((root / "curriculum/curriculum.json").read_text(encoding="utf8"))
        quests = json.loads((root / "curriculum/side-quests.json").read_text(encoding="utf8"))
    except (OSError, ValueError) as e:
        return [f"Invalid curriculum JSON: {e}"]
    modules = data.get("modules", [])
    ids = [x.get("id") for x in modules]
    if len(ids) != 14 or ids != [f"{i:02}" for i in range(14)]:
        errors.append(f"Expected ordered stages 00–13, got {ids}")
    if len(set(ids)) != len(ids):
        errors.append("Duplicate module IDs")
    for m in modules:
        mod = root / m["module"]
        if not mod.is_file():
            errors.append(f"Missing file: {m['module']}")
        for p in m["prerequisites"]:
            if p not in ids or ids.index(p) >= ids.index(m["id"]):
                errors.append(f"Bad prerequisite {p} for {m['id']}")
    for quest in quests:
        if quest.get("stage") not in ids:
            errors.append(f"Quest stage not found: {quest.get('stage')}")
        if not (10 <= quest.get("minutes", 0) <= 25):
            errors.append("Quest should take 10–25 minutes")
        if not (root / "curriculum/cs-bridges" / f"{quest['cs']}.md").exists():
            errors.append(f"Missing CS bridge: {quest['cs']}")
    for needed in ["README.md", "README.en.md", "AGENTS.md", "LICENSE", "SECURITY.md",
                   "prompts/MASTER-AGENT.he.md", "prompts/MASTER-AGENT.en.md",
                   "docs/GITHUB-MCP-SETUP.he.md", "docs/ASSESSMENT.md", "docs/ENVIRONMENT.he.md",
                   "scripts/system_profile.py", "scripts/roadmap.py", "projects/datapulse/README.md"]:
        if not (root / needed).is_file():
            errors.append(f"Missing required file: {needed}")
    # Links are local; ignore absolute HTTP, anchors, mailto. Never fetch remote content.
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for md in root.rglob("*.md"):
        if any(x in md.parts for x in (".venv", ".git")):
            continue
        for target in pattern.findall(md.read_text(encoding="utf8")):
            target = target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not (md.parent / target).exists():
                errors.append(f"Broken local link in {md.relative_to(root)}: {target}")
    errors.extend(validate_learning_assets(root))
    return errors


def validate_learning_assets(root=ROOT):
    """Check self-contained notebook and illustration assets using stdlib only."""
    errors = []
    for name in ("hero.svg", "learning-loop.svg"):
        asset = root / "assets" / name
        if not asset.is_file():
            errors.append(f"Missing original diagram asset: {name}")
            continue
        content = asset.read_text(encoding="utf8")
        if "<svg" not in content or "<title" not in content or "<desc" not in content:
            errors.append(f"SVG lacks accessible title/description: {name}")
    for name in ("00_data_journey.ipynb", "01_sql_detective.ipynb", "02_etl_failure_lab.ipynb", "03_pipeline_observatory.ipynb"):
        file = root / "notebooks" / name
        if not file.is_file():
            errors.append(f"Missing educational notebook: {name}")
            continue
        try:
            notebook = json.loads(file.read_text(encoding="utf8"))
            cells = notebook["cells"]
            assert notebook["nbformat"] == 4
            assert sum(c["cell_type"] == "code" for c in cells) >= 2
            sources = "\n".join("".join(c["source"]) if isinstance(c["source"], list) else c["source"] for c in cells)
            assert "youtube.com/watch?v=" in sources  # clickable fallback
            assert "YouTubeVideo(" in sources  # optional Jupyter embed
            assert "assert " in sources  # executable check
            assert "Goal:" in sources and "Next" in sources
        except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
            errors.append(f"Notebook invalid or missing education/fallback/check: {name} ({exc})")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("Validation failed:\n- " + "\n- ".join(failures), file=sys.stderr)
        sys.exit(1)
    print("PASS: curriculum 00–13, links, CS bridges, side quests and mandatory files")
