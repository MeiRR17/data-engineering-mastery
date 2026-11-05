"""Validate a candidate's evidence structure; never issue credentials or certify.

This script checks declared scores and local evidence files only.
Reviewer signatures, originality and external claims are NOT verified by code.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
FIELDS=("concepts","implementation","testing","architecture","operations")


def _evidence(path, root):
    if not isinstance(path,str) or not path or len(path)>240:
        return False
    candidate=Path(path)
    if candidate.is_absolute() or any(x in ("..",".") for x in candidate.parts):
        return False
    item=(root/candidate).resolve()
    # Symlinks and external/nonexistent paths cannot satisfy an evidence gate.
    if not item.is_relative_to(root.resolve()):
        return False
    if not item.is_file() or item.is_symlink():
        return False
    if item.stat().st_size>10_000_000 or item.stat().st_size==0:
        return False
    return True


def evaluate(path):
    path=Path(path)
    blueprint=json.loads((ROOT/"blueprint.json").read_text(encoding="utf8"))
    try:
        submission=json.loads(path.read_text(encoding="utf8"))
    except (OSError,ValueError) as exc:
        raise ValueError("invalid submission JSON") from exc
    if not isinstance(submission,dict):
        raise ValueError("submission must be an object")
    issues=[]
    stages=submission.get("stages",{})
    expected=[x["id"] for x in blueprint["stages"]]
    if not isinstance(stages,dict):
        stages={}
        issues.append("stage evidence must be a mapping")
    if set(stages)!=set(expected):
        issues.append("exactly 14 stages 00..13 are required")
    score_gate=blueprint["mandatory_score_at_least"]
    passed=0
    for id in expected:
        entry=stages.get(id)
        if not isinstance(entry,dict):
            issues.append(f"stage {id}: missing entry")
            continue
        valid=True
        scores=entry.get("scores",{})
        if not isinstance(scores,dict) or set(scores)!=set(FIELDS):
            issues.append(f"stage {id}: invalid score set")
            continue
        for key in FIELDS:
            n=scores[key]
            if type(n) is not int or not 0<=n<=4:
                issues.append(f"stage {id}: invalid {key} score")
                valid=False
        if not valid:
            continue
        for key,min_score in score_gate.items():
            if scores[key]<min_score:
                issues.append(f"stage {id}: {key} below minimum {min_score}")
                valid=False
        if id=="13" and min(scores.values())<3:
            issues.append("stage 13: all five rubric dimensions must reach 3")
            valid=False
        evidence=entry.get("evidence",[])
        if not isinstance(evidence,list) or len(evidence)<3 or len(evidence)>20:
            issues.append(f"stage {id}: provide three or more local evidence files")
            valid=False
        elif not all(_evidence(x,path.parent) for x in evidence):
            issues.append(f"stage {id}: evidence missing, empty, unsafe or outside submission")
            valid=False
        if entry.get("independent_transfer") is not True:
            issues.append(f"stage {id}: independent transfer unverified")
            valid=False
        findings=entry.get("critical_findings")
        if not isinstance(findings,list):
            issues.append(f"stage {id}: invalid findings list")
            valid=False
        elif findings:
            issues.append(f"stage {id}: unresolved critical findings")
            valid=False
        if valid:
            passed+=1
    exam=submission.get("final_exam",{})
    if not isinstance(exam,dict):
        exam={}
    expected_sections=blueprint["final_exam"]["section_maximums"]
    score=0
    if set(exam)!=set(expected_sections):
        issues.append("all four exam scores are required")
    else:
        for key,maximum in expected_sections.items():
            value=exam[key]
            if type(value) is not int or not 0<=value<=maximum:
                issues.append(f"exam: invalid {key} score")
            else:
                score+=value
                if value<blueprint["final_exam"]["minimum_sections"][key]:
                    issues.append(f"exam: {key} below section minimum")
    if score<blueprint["final_exam"]["passing_score"]:
        issues.append("exam: score below 80")
    reviewer=submission.get("reviewer",{})
    if (not isinstance(reviewer,dict) or
        not isinstance(reviewer.get("name"),str) or
        not 2<=len(reviewer.get("name","").strip())<=120 or
        reviewer.get("independent_review_completed") is not True or
        reviewer.get("capstone_demonstrated") is not True):
        issues.append("qualified independent reviewer and witnessed capstone required")
    claims=submission.get("external_claims",{})
    if not isinstance(claims,dict) or set(claims)!={
        "cloud_deployed","kafka_broker_run","spark_runtime_run"
    } or any(type(v) is not bool for v in claims.values()):
        issues.append("external claims must explicitly declare three booleans")
    elif not claims["kafka_broker_run"] or not claims["spark_runtime_run"]:
        issues.append("full-mode Kafka broker and PySpark evidence not declared")
    if submission.get("schema_version")!=1:
        issues.append("submission schema version unsupported")
    alias=submission.get("candidate_alias")
    if not isinstance(alias,str) or not 3<=len(alias.strip())<=100:
        issues.append("candidate alias required (no account identifier needed)")
    return {
        "status":"needs_evidence" if issues else "ready_for_human_review",
        "stages_with_structurally_valid_evidence":passed,
        "stages_required":14,
        "exam_score_self_reported":score,
        "issues":issues[:120],
        "caveat":"Machine check only. No authorship, rubric truth, reviewer identity or cloud evidence was independently validated. No certificate issued.",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission",type=Path)
    args=parser.parse_args()
    report=evaluate(args.submission)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report["status"]=="ready_for_human_review" else 1


if __name__=="__main__":
    raise SystemExit(main())

