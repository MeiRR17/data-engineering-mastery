"""Create deterministic unseen transfer prompts and a separate reviewer answer key.

Use a NEW output directory. This is exam material generation, not invigilation.
Never upload reviewer_only files to the student's repository.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
from random import Random


def generate(seed,output):
    if type(seed) is not int or not 1<=seed<=2**63-1:
        raise ValueError("seed must be positive integer")
    output=Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError("exam output must not already exist")
    rng=Random(seed)
    region=rng.choice(["N","E","W","S"])
    day=rng.randrange(1,22)
    base=datetime(2026,1,day,10,0,tzinfo=timezone.utc)
    magnitude_a=rng.choice([1.2,2.4,3.6,4.8])
    magnitude_b=rng.choice([2.3,4.1,5.7,6.2])
    late=rng.choice([1.8,3.4,4.9,5.5])
    start=base.strftime("%Y-%m-%dT%H:%M:%SZ")
    revised=(base+timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated=(base+timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows=[
        {"event_id":"transfer-A","observed_at":start,
         "source_updated_at":(base+timedelta(minutes=5)).isoformat(),
         "region_code":region,"magnitude":magnitude_a},
        {"event_id":"transfer-B","observed_at":(base+timedelta(minutes=30)).isoformat(),
         "source_updated_at":(base+timedelta(minutes=31)).isoformat(),
         "region_code":region,"magnitude":magnitude_b},
        {"event_id":"transfer-A","observed_at":start,
         "source_updated_at":updated,"region_code":region,"magnitude":late},
        {"event_id":"transfer-C","observed_at":revised,
         "source_updated_at":(base+timedelta(hours=2,minutes=5)).isoformat(),
         "region_code":"Q","magnitude":None},
        {"event_id":"transfer-D","observed_at":start,
         "source_updated_at":updated,"region_code":"bad-region","magnitude":9},
    ]
    rng.shuffle(rows)
    prompt=f"""# Independent transfer examination — candidate material

This is a newly generated **synthetic** event set; all results should come from your own implementation. Do not request the reviewer-only answer key.

## Tasks

1. Write SQL (or explain its schema) to deduplicate the source by event_id, using source_updated_at to choose newer corrections. Show the correct grain and what happens if you JOIN a Type 2 dimension without an as-of predicate.
2. Implement a safe Python parse/normalize path. Quarantine structurally invalid rows with reason codes only. Treat NULL magnitude as missing measurement, not as zero.
3. Compute the count of unique accepted events and the magnitude average for region {region} on the UTC date. Explain late/out-of-order source updates.
4. Propose a Kafka consumer checkpoint and local sink transaction plan for replay after a lost acknowledgement.
5. Incident scenario: Dashboard freshness is 36 hours while SLO threshold is 24h. Write an operator's first ten minutes of response, including data-quality, rollback and restore decision gates.
6. Defend the design to an examiner: when does Spark become justified vs PostgreSQL or DuckDB for a 50 MB/day source? Include a proposed benchmark.

Candidate must provide code, tests, clean logs, a short ADR and a no-AI explanation. Reference time: {start}.
"""
    candidate=output/"candidate"
    examiner=output/"reviewer_only"
    candidate.mkdir(parents=True)
    examiner.mkdir(parents=True)
    (candidate/"instructions.md").write_text(prompt,encoding="utf8")
    (candidate/"events.jsonl").write_text(
        "\n".join(json.dumps(x,sort_keys=True) for x in rows)+"\n",encoding="utf8"
    )
    (candidate/"regions.csv").write_text(
        "region_code,region_name,valid_from,valid_to\n"+
        f"{region},Region Legacy,2025-01-01T00:00:00Z,{revised}\n"+
        f"{region},Region Current,{revised},\n",encoding="utf8"
    )
    (candidate/"incident.json").write_text(
        json.dumps({"data_age_hours":36,"freshness_slo_hours":24,
                    "last_batch":"failed","backup_available":True},indent=2)+"\n"
    )
    key={
        "seed":seed,"region":region,"valid_rows":4,"invalid_rows":1,
        "unique_valid_events":3,
        "known_magnitudes_in_region":2,
        "regional_average":round((late+magnitude_b)/2,2),
        "invalid_reason":"INVALID_REGION",
        "source_revision_selected":"transfer-A latest source_updated_at",
        "all_null_region":"Q",
        "required_incident_labels":["freshness","rollback","checkpoint","restore","SLO"],
        "security_note":"Do not copy reviewer-only answer key to candidate folder.",
    }
    (examiner/"answer_key.json").write_text(
        json.dumps(key,sort_keys=True,indent=2)+"\n",encoding="utf8"
    )
    (examiner/"README.md").write_text(
        "Reviewer only. Verify authorship, offer a new failure-mode question, "
        "review code and mark rubric. This generator does not grade the exam.\n"
    )
    return {
        "status":"generated","candidate_folder":str(candidate),
        "reviewer_only_folder":str(examiner),
        "warning":"Keep reviewer_only private until assessment ends."
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed",type=int,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(generate(args.seed,args.output),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

