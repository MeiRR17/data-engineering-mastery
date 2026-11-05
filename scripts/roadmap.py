#!/usr/bin/env python3
"""Local-only self-reported learner progress. No GitHub/network calls or cloud secrets."""
from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum" / "curriculum.json"
STATE = ROOT / "learner" / "progress.json"  # explicitly excluded from Git


def load_curriculum():
    return json.loads(CURRICULUM.read_text(encoding="utf8"))["modules"]


def load_state():
    if not STATE.exists():
        raise ValueError("No local progress file; run: python3 scripts/roadmap.py init --alias learner")
    data = json.loads(STATE.read_text(encoding="utf8"))
    if not isinstance(data.get("completed"), dict):
        raise ValueError("Invalid learner progress format")
    return data


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    try:
        STATE.chmod(0o600)
    except OSError:
        pass


def get_module(modules, module_id):
    for m in modules:
        if m["id"] == module_id:
            return m
    raise ValueError(f"Unknown stage {module_id}; valid: {', '.join(m['id'] for m in modules)}")


def require_prereqs(module, state):
    missing = [p for p in module["prerequisites"] if p not in state["completed"]]
    if missing:
        raise ValueError(f"Complete prerequisites first: {', '.join(missing)}")


def first_next(modules, state):
    return next((m for m in modules if m["id"] not in state["completed"]), None)


def init(alias):
    if STATE.exists():
        raise ValueError("Local progress exists: refusing overwrite. Back it up if you need to reset.")
    alias = alias.strip()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,48}", alias):
        raise ValueError("Alias must be 1–48 letters/numbers/_/- only (not a real name)")
    save_state({"schema_version": "1.0.0", "learner_alias": alias,
                "completed": {}, "in_progress": None})
    print("Created private learner/progress.json (gitignored). Next: roadmap.py status")


def status(modules, state):
    done = state["completed"]
    print(f"Learner alias: {state['learner_alias']}")
    print(f"Self-reported stages: {len(done)}/{len(modules)} ({len(done)/len(modules)*100:.1f}%)")
    print("This is a learning record, NOT independent verification or certification.")
    print(f"Current: {state.get('in_progress') or 'not set'}")
    for m in modules:
        label = "SELF-REPORTED" if m["id"] in done else ("ACTIVE" if m["id"] == state.get("in_progress") else "PENDING")
        print(f"  [{label:13s}] {m['id']}  {m['title']}")
    nxt = first_next(modules, state)
    if nxt:
        print(f"Recommended next: {nxt['id']} {nxt['title']} ({nxt['module']})")
    else:
        print("All stages self-reported. Seek independent capstone review and pursue advanced specialization.")


def next_stage(modules, state):
    m = first_next(modules, state)
    if not m:
        print("All modules self-reported complete; see docs/ROADMAP.he.md for advanced paths.")
        return
    print(f"Stage {m['id']}: {m['title']}\nModule: {m['module']}\nDeliverable: {m['deliverable']}\nExit: {m['exit_criteria']}")
    q = json.loads((ROOT / "curriculum" / "side-quests.json").read_text(encoding="utf8"))
    quest = next((x for x in q if x["stage"] == m["id"]), None)
    if quest:
        print(f"Optional side quest ({quest['minutes']} min): {quest['title']} — {quest['challenge']}")


def start(module_id, modules, state):
    m = get_module(modules, module_id)
    require_prereqs(m, state)
    if module_id in state["completed"]:
        raise ValueError("This stage is already self-reported complete")
    state["in_progress"] = module_id
    save_state(state)
    print(f"Stage {module_id} is active. Read {m['module']}; start with a small independent attempt.")


def complete(module_id, evidence, reflection, quiz_notes, modules, state):
    m = get_module(modules, module_id)
    require_prereqs(m, state)
    if module_id in state["completed"]:
        raise ValueError("Already self-reported complete; do not overwrite evidence")
    if len(evidence.strip()) < 4 or len(reflection.strip()) < 40 or len(quiz_notes.strip()) < 12:
        raise ValueError("Provide evidence (4+ chars), thoughtful reflection (40+ chars), and quiz notes (12+ chars)")
    state["completed"][module_id] = {
        "evidence": evidence.strip(), "reflection": reflection.strip(),
        "quiz_notes": quiz_notes.strip(),
        "recorded_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "verification": "self_reported_not_independently_verified",
    }
    if state["in_progress"] == module_id:
        state["in_progress"] = None
    save_state(state)
    print(f"Stage {module_id} recorded as SELF-REPORTED only. Request a review under docs/ASSESSMENT.md.")
    next_stage(modules, state)


def export_summary(modules, state):
    """Explicit, sanitized GitHub-readable snapshot; NEVER publishes automatically."""
    output = ROOT / "learner" / "learning-status.md"
    nxt = first_next(modules, state)
    completed = sorted(state["completed"], key=int)
    content = (
        "# Learning status (opt-in, self-reported)\n\n"
        "This file contains only stage IDs and titles. It is NOT an independent assessment.\n"
        "Review before you voluntarily commit it to your own repository.\n\n"
        f"Completed (self-reported): {', '.join(completed) if completed else 'none'}\n\n"
        f"Current stage: {state.get('in_progress') or 'none'}\n\n"
        f"Next suggested stage: {(nxt['id'] + ' — ' + nxt['title']) if nxt else 'advanced specialization'}\n"
    )
    output.write_text(content, encoding="utf8")
    print("Wrote learner/learning-status.md. Nothing was uploaded. Review it before optional commit to YOUR learner repo.")


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init", help="Initialize local/private progress (no reset)")
    p.add_argument("--alias", default="learner")
    sub.add_parser("status")
    sub.add_parser("next")
    sub.add_parser("export-summary", help="Create a sanitized, optional GitHub-readable status file locally")
    p = sub.add_parser("start")
    p.add_argument("stage")
    p = sub.add_parser("complete")
    p.add_argument("stage")
    p.add_argument("--evidence", required=True)
    p.add_argument("--reflection", required=True)
    p.add_argument("--quiz-notes", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            init(args.alias)
            return
        modules = load_curriculum()
        state = load_state()
        if args.command == "status":
            status(modules, state)
        elif args.command == "next":
            next_stage(modules, state)
        elif args.command == "export-summary":
            export_summary(modules, state)
        elif args.command == "start":
            start(args.stage, modules, state)
        elif args.command == "complete":
            complete(args.stage, args.evidence, args.reflection, args.quiz_notes, modules, state)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        parser.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    cli()
