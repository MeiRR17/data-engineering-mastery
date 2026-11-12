#!/usr/bin/env python3
"""Private, offline spaced-review scheduler for curriculum stages 00–13.

This is a self-study reminder, not a skills assessment or certificate.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "learner" / "reviews.local.json"  # gitignored; no network or account access
CURRICULUM = ROOT / "curriculum" / "curriculum.json"
INTERVALS = (1, 3, 7, 14, 30)


def parse_day(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid calendar date") from exc


def allowed_stages(path: Path = CURRICULUM) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {m["id"] for m in data["modules"]}


def load_state(path: Path = STATE) -> dict:
    if path.is_symlink():
        raise ValueError("refusing to follow a local review-state symlink")
    if not path.exists():
        return {"schema_version": 1, "cards": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("cards"), dict):
        raise ValueError("invalid review-state schema; original file left unchanged")
    for stage, card in data["cards"].items():
        if not re.fullmatch(r"\d{2}", stage) or not isinstance(card, dict):
            raise ValueError("invalid review-stage record")
        step, count = card.get("step"), card.get("count")
        if type(step) is not int or not -1 <= step < len(INTERVALS) or type(count) is not int or count < 0:
            raise ValueError("invalid review interval or count")
        parse_day(card.get("due", ""))
        last = card.get("last_review")
        if last is not None:
            parse_day(last)
    return data


def save_state(data: dict, path: Path = STATE) -> None:
    """Atomically replace only the gitignored local state; private permissions on POSIX."""
    if path.is_symlink():
        raise ValueError("refusing to replace a local review-state symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=".reviews-", suffix=".tmp", delete=False) as stream:
            temp_name = stream.name
            os.chmod(temp_name, 0o600)
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def add_stage(data: dict, stage: str, today: date, stages: set[str]) -> dict:
    if stage not in stages:
        raise ValueError(f"unknown curriculum stage: {stage}")
    if stage in data["cards"]:
        raise ValueError(f"stage {stage} is already scheduled; refusing to overwrite progress")
    data["cards"][stage] = {"step": -1, "count": 0, "due": today.isoformat(), "last_review": None}
    return data


def record_review(data: dict, stage: str, rating: str, today: date) -> dict:
    if stage not in data["cards"]:
        raise ValueError(f"stage {stage} is not scheduled; use add first")
    if rating not in ("again", "hard", "good", "easy"):
        raise ValueError("rating must be again, hard, good, or easy")
    card = data["cards"][stage]
    previous = parse_day(card["last_review"]) if card["last_review"] else None
    if previous is not None and today <= previous:
        raise ValueError("one review per stage per day; cannot backdate a review")
    old_step = card["step"]
    if rating == "again":
        step = 0
    elif rating == "hard":
        step = max(0, old_step)
    elif rating == "good":
        step = min(len(INTERVALS) - 1, old_step + 1)
    else:
        step = min(len(INTERVALS) - 1, old_step + 2)
    card.update(step=step, count=card["count"] + 1,
                last_review=today.isoformat(), due=(today + timedelta(days=INTERVALS[step])).isoformat())
    return data


def due_stages(data: dict, today: date) -> list[tuple[str, int]]:
    items = [(stage, (today - parse_day(card["due"])).days)
             for stage, card in data["cards"].items() if parse_day(card["due"]) <= today]
    return sorted(items, key=lambda item: (-item[1], item[0]))


def show_status(data: dict, today: date, show_all: bool = False) -> str:
    due = due_stages(data, today)
    lines = [f"Spaced review | {today.isoformat()} | {len(due)} due of {len(data['cards'])} stages",
             "Private local reminder only; not a verified competency assessment."]
    for stage, late in due:
        lines.append(f"  {stage}  {'today' if late == 0 else f'{late}d overdue'}")
    if show_all:
        upcoming = sorted(((card["due"], stage) for stage, card in data["cards"].items()
                           if parse_day(card["due"]) > today))
        lines.extend(f"  {stage}  upcoming {day}" for day, stage in upcoming)
    if not data["cards"]:
        lines.append("No reviews yet. Add a stage with: python3 scripts/spaced_review.py add 00")
    elif not due:
        lines.append("No reviews due today.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="command", required=True)
    for name in ("add", "review", "due"):
        p = actions.add_parser(name)
        if name != "due":
            p.add_argument("stage", help="Curriculum stage 00–13")
        if name == "review":
            p.add_argument("rating", choices=("again", "hard", "good", "easy"))
        if name == "due":
            p.add_argument("--all", action="store_true", help="Also show upcoming review dates")
        p.add_argument("--on", metavar="YYYY-MM-DD", help="Override today's date for offline planning")
    args = parser.parse_args(argv)
    try:
        today = parse_day(args.on) if args.on else date.today()
        data = load_state()
        if args.command == "add":
            add_stage(data, args.stage, today, allowed_stages())
            save_state(data)
            print(f"Scheduled stage {args.stage} for {today.isoformat()} (local only).")
        elif args.command == "review":
            record_review(data, args.stage, args.rating, today)
            save_state(data)
            print(f"Stage {args.stage}: next review {data['cards'][args.stage]['due']} (local only).")
        else:
            print(show_status(data, today, args.all))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
