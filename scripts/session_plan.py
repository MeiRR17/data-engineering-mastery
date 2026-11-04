#!/usr/bin/env python3
"""Deterministic, offline session brief for an AI tutor. No data is sent anywhere."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def make_plan(style='investigator', level='intermediate', minutes=60, root=ROOT):
    curriculum=json.loads((root/'curriculum/curriculum.json').read_text(encoding='utf8'))['modules']
    quests=json.loads((root/'curriculum/side-quests.json').read_text(encoding='utf8'))
    progress=root/'learner/progress.json'
    completed={}
    current=None
    if progress.exists():
        state=json.loads(progress.read_text(encoding='utf8'))
        completed=state.get('completed',{})
        current=state.get('in_progress')
    stage=next((m for m in curriculum if m['id']==current),None)
    if stage is None:
        stage=next((m for m in curriculum if m['id'] not in completed), curriculum[-1])
    quest=next((q for q in quests if q['stage']==stage['id']),None)
    profile_path=root/'learner/system-profile.local.json'
    tier='unknown (use conservative light environment until learner opts in)'
    if profile_path.exists():
        profile=json.loads(profile_path.read_text(encoding='utf8'))
        tier=profile.get('resource_tier','unknown')
    lesson=min(10,max(5,round(minutes*.15)))
    reflection=min(10,max(5,round(minutes*.1)))
    independent=max(10,minutes-lesson-reflection)
    hooks={
        'investigator':'Start with a puzzling data discrepancy; ask for hypotheses before showing tools',
        'builder':'Define a small interface and test; learner writes first implementation',
        'debugger':'Present an intentionally failing test; learner locates and explains root cause',
        'production':'Present a failure mode and SLO; learner weighs reliability, security and cost',
    }
    difficulty={
        'beginner':'short scaffolded exercise + 2 hints at most before checkpoint',
        'intermediate':'independent implementation + edge case + explain a tradeoff',
        'advanced':'unfamiliar failure injection + performance measurement + ADR',
    }
    return {'stage':stage['id'],'title':stage['title'],'module':stage['module'],
            'deliverable':stage['deliverable'],'exit_criteria':stage['exit_criteria'],
            'style':style,'hook':hooks[style], 'difficulty':difficulty[level],
            'minutes':minutes,'micro_lesson_min':lesson,'independent_lab_min':independent,
            'reflection_min':reflection,'resource_tier':tier,
            'side_quest':quest,'cs_bridge':f"curriculum/cs-bridges/{quest['cs']}.md" if quest else None,
            'next_action':'Read module, predict an outcome, write code yourself, run reproducible tests and explain tradeoffs',
            'notes':'This plan is only a learning suggestion; it does not certify competence or inspect private data.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--style',choices=['investigator','builder','debugger','production'],default='investigator')
    p.add_argument('--level',choices=['beginner','intermediate','advanced'],default='intermediate')
    p.add_argument('--minutes',type=int,default=60)
    args=p.parse_args()
    if not (20 <= args.minutes <= 180):
        p.error('--minutes must be 20–180')
    print(json.dumps(make_plan(args.style,args.level,args.minutes),indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
