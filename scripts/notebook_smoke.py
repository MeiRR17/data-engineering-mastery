
"""Run Stage 04–13 teaching notebook code cells without a Jupyter server.

Uses Python standard library and isolated per-notebook namespaces; these are
synthetic examples, not the graded student exercises. No network or Docker.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
NAMES=[
    "04_postgres_security.ipynb",
    "05_scd2_modeling.ipynb",
    "06_dag_recovery.ipynb",
    "07_quality_contracts.ipynb",
    "08_readonly_serving.ipynb",
    "09_releases_rollback.ipynb",
    "10_spark_partitioning.ipynb",
    "11_streaming_offsets.ipynb",
    "12_slo_recovery.ipynb",
    "13_integrated_capstone.ipynb",
]


def smoke(root=ROOT):
    results=[]
    for name in NAMES:
        path=root/"notebooks"/name
        data=json.loads(path.read_text(encoding="utf8"))
        if data.get("nbformat")!=4:
            raise ValueError(f"Not a modern notebook: {name}")
        env={"__name__":"__main__","__file__":str(path)}
        cells=[c for c in data["cells"] if c.get("cell_type")=="code"]
        if len(cells)<2:
            raise ValueError(f"Notebook requires two executable checks: {name}")
        for index,cell in enumerate(cells,1):
            source=cell["source"]
            if isinstance(source,list):
                source="".join(source)
            exec(compile(source,f"{name}:cell{index}","exec"),env)
        results.append(name)
    return results


if __name__=="__main__":
    complete=smoke()
    print(f"PASS: {len(complete)} offline Stage 04–13 notebooks executed")
