# Interactive learning notebooks — 14 stages (00–13)

[Return to repository](../README.md) · [Course map](../docs/training-manifest.json) · [Assessment](../docs/FINAL-ASSESSMENT.he.md)

All **14 stages have a guided notebook**. Notebooks 00–03 include external video links and optional embeds; notebooks 04–13 use official documentation links and small, synthetic, **Python standard-library-only** examples, without network or external credentials.

## How to learn from a notebook

1. In VS Code + Jupyter or JupyterLab, open the matching file and read the **Goal** and the prediction prompt.
2. Before running a code cell, write your predicted result, including one failure mode.
3. Run the cells (Run All) and change one safe synthetic input. Explain why an assertion succeeds or fails.
4. Open the matching `labs/XX-*/README.md`, implement the **independent starter**, pass the stage grader, and write a short reflection.
5. Complete an unseen transfer scenario without AI before marking that stage complete. Watching a video or passing notebook examples alone does not demonstrate mastery.

## Notebook index

| Stage | Notebook | Concept |
|---|---|---|
| 00 | [Data journey](00_data_journey.ipynb) | End-to-end event flow and engineering vocabulary |
| 01 | [SQL detective](01_sql_detective.ipynb) | Relational reasoning, joins, nulls |
| 02 | [ETL failure lab](02_etl_failure_lab.ipynb) | Parsing and source errors |
| 03 | [Pipeline observatory](03_pipeline_observatory.ipynb) | Monitoring and failure detection |
| 04 | [PostgreSQL security](04_postgres_security.ipynb) | Read-only behavior vs RLS |
| 05 | [SCD2 modeling](05_scd2_modeling.ipynb) | As-of historical joins and double-counting |
| 06 | [DAG recovery](06_dag_recovery.ipynb) | Dependencies, backfill windows |
| 07 | [Quality contracts](07_quality_contracts.ipynb) | Completeness/validity gates |
| 08 | [Read-only serving](08_readonly_serving.ipynb) | Correct averages and access boundaries |
| 09 | [Release/rollback](09_releases_rollback.ipynb) | Artifact integrity and health gates |
| 10 | [Spark partitioning](10_spark_partitioning.ipynb) | Hash partitioning and skew |
| 11 | [Streaming offsets](11_streaming_offsets.ipynb) | Checkpoint atomicity and replay |
| 12 | [SLO recovery](12_slo_recovery.ipynb) | Error budgets and stale data |
| 13 | [Integrated capstone](13_integrated_capstone.ipynb) | Real integrated **local** reference pipeline |

## Environment

For the new 04–13 notebooks, Python 3.11+ is sufficient for code cells, along with a Jupyter-capable editor if interactive viewing is desired. **Jupyter itself is optional**: the source snippets are also executable without a Jupyter runtime using:

~~~bash
python3 scripts/notebook_smoke.py
python3 scripts/audit_program.py
~~~

These commands test all ten new advanced notebooks and the 14-stage course file map. Notebooks 00–03 have richer video/chart content and may require optional IPython and Matplotlib; [notebooks/requirements.txt](requirements.txt) is for a dedicated virtual environment.

**Important:** The notebook smoke script runs instructor *tutorials*, not learner starter solutions. Full PostgreSQL, dbt, Spark and Kafka exercises are separately tested by CI jobs where Docker/JVM and dependencies are available. Do not claim that an offline notebook proves cloud or multi-node competence.

Video assets are only linked to the original providers. No copyrighted videos are hosted or copied into this repository.
