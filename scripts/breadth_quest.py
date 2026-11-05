#!/usr/bin/env python3
"""Small, offline curriculum explorer for cross-discipline quests.

This command never probes the machine and never accesses learner progress.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST_PATH = ROOT / "curriculum" / "breadth-quests.json"
STAGES = {f"{index:02d}" for index in range(14)}
REQUIRED = {"id", "domain", "title_he", "stages", "minutes", "question",
            "experiment", "evidence", "transfer", "requirements"}

def load_quests(path=QUEST_PATH):
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    return content["quests"]

def validate_quests(quests):
    errors = []
    ids = set()
    coverage = set()
    for quest in quests:
        identifier = quest.get("id", "<missing>")
        missing = REQUIRED - set(quest)
        if missing:
            errors.append(f"{identifier}: missing {sorted(missing)}")
        if identifier in ids:
            errors.append(f"duplicate id: {identifier}")
        ids.add(identifier)
        stages = quest.get("stages", [])
        if not stages or any(stage not in STAGES for stage in stages):
            errors.append(f"{identifier}: invalid stages {stages}")
        coverage.update(stage for stage in stages if stage in STAGES)
        if not isinstance(quest.get("minutes"), int) or not 15 <= quest["minutes"] <= 90:
            errors.append(f"{identifier}: minutes must be 15..90")
        for field in ["question", "experiment", "evidence", "transfer", "requirements"]:
            if not isinstance(quest.get(field), str) or len(quest[field].strip()) < 12:
                errors.append(f"{identifier}: incomplete {field}")
    if coverage != STAGES:
        errors.append(f"missing stage coverage: {sorted(STAGES - coverage)}")
    return errors

def show(quest):
    for field, label in [
        ("title_he", "אתגר"), ("domain", "תחום"),
        ("question", "שאלת חקר"), ("experiment", "ניסוי"),
        ("evidence", "הוכחה"), ("transfer", "מבחן העברה"),
        ("requirements", "משאבים"),
    ]:
        print(f"{label}: {quest[field]}")
    print(f"Stage: {', '.join(quest['stages'])} | דקות: {quest['minutes']}")

def main():
    parser = argparse.ArgumentParser(description="Offline breadth-quest explorer")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("list", help="List all breadth quests")
    rec = subs.add_parser("recommend", help="Select quests for a data stage")
    rec.add_argument("--stage", required=True, choices=sorted(STAGES))
    rec.add_argument("--limit", type=int, default=2)
    detail = subs.add_parser("show", help="Show a quest")
    detail.add_argument("id")
    subs.add_parser("check", help="Validate the quest manifest")
    args = parser.parse_args()
    quests = load_quests()
    errors = validate_quests(quests)
    if errors:
        for item in errors:
            print("ERROR:", item)
        return 1
    if args.command == "check":
        print(f"OK: {len(quests)} quests cover {len(STAGES)} stages.")
    elif args.command == "list":
        for quest in quests:
            print(f"{quest['id']} ({'/'.join(quest['stages'])}) {quest['title_he']}")
    elif args.command == "recommend":
        if args.limit < 1:
            parser.error("--limit must be positive")
        candidates = [q for q in quests if args.stage in q["stages"]]
        for quest in candidates[:args.limit]:
            print(f"{quest['id']}: {quest['title_he']} — {quest['minutes']} דקות")
    else:
        matching = next((q for q in quests if q["id"] == args.id), None)
        if matching is None:
            parser.error(f"unknown quest: {args.id}")
        show(matching)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
