
"""Audit whether all 14 stages have code, notebook, grader, and an exit path.

This is a **structural** audit, not an academic/accreditation certificate.
It does not execute Docker, cloud services, Spark or Kafka by itself.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    root=Path(root)
    errors=[]
    meta_path=root/"docs/training-manifest.json"
    if not meta_path.is_file():
        return {"status":"incomplete","errors":["training manifest missing"]}
    try:
        manifest=json.loads(meta_path.read_text(encoding="utf8"))
        entries=manifest["stages"]
    except (OSError,KeyError,ValueError,TypeError) as exc:
        return {"status":"incomplete","errors":["invalid training manifest: "+str(exc)]}
    identifiers=[s.get("id") for s in entries]
    expected=[f"{i:02}" for i in range(14)]
    if identifiers!=expected:
        errors.append("expected exactly 14 sequential stages 00–13")
    for stage in entries:
        sid=stage.get("id","unknown")
        for attr in ("module","lab","readme","notebook"):
            path=stage.get(attr)
            if not isinstance(path,str) or not (root/path).exists():
                errors.append(f"{sid}: missing {attr}: {path}")
        grade=stage.get("grader","")
        if not isinstance(grade,str) or not grade.startswith("python3 "):
            errors.append(f"{sid}: invalid grader command")
        else:
            token=grade.split()[1]
            if not (root/token).is_file():
                errors.append(f"{sid}: missing grader {token}")
        if stage.get("prerequisites")!=([] if sid=="00" else
                                      [f"{int(sid)-1:02}"]):
            errors.append(f"{sid}: prerequisite mismatch")
        course=(root/stage.get("module","nonexistent"))
        if course.exists():
            content=course.read_text(encoding="utf8")
            if len(content)<500:
                errors.append(f"{sid}: course content too sparse")
            if not any(word in content.lower() for word in ("exit","מעבר","gate")):
                errors.append(f"{sid}: missing assessment gate in course")
        lab=(root/stage.get("readme","nonexistent"))
        if lab.exists() and len(lab.read_text(encoding="utf8"))<400:
            errors.append(f"{sid}: lab guide too sparse")
    mandatory=[
        "docs/ASSESSMENT.md","docs/FINAL-ASSESSMENT.he.md",
        "assessment/evaluate.py","assessment/generate_transfer.py",
        "capstone/specification.md","capstone/grade.py",
        "scripts/notebook_smoke.py",
        ".github/workflows/ci.yml",
    ]
    for path in mandatory:
        if not (root/path).is_file():
            errors.append("missing required program asset "+path)
    return {
        "status":"structure_verified" if not errors else "incomplete",
        "stages":len(entries),
        "notebooks":sum((root/s.get("notebook","missing")).is_file() for s in entries),
        "lab_guides":sum((root/s.get("readme","missing")).is_file() for s in entries),
        "grader_files":sum((root/s.get("grader","missing").split()[1]).is_file()
                           for s in entries if len(s.get("grader","").split())>=2),
        "errors":errors,
        "external_gates_not_verifiable_by_this_script":[
            "real independent learner completes new unseen practical exam",
            "qualified human checks authorship and project transfer",
            "optional production-like cloud sandbox security/deploy/restore",
            "third-party accreditation does not exist"
        ],
    }


if __name__=="__main__":
    report=audit()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report["status"]=="structure_verified" else 1)
