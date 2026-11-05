# Jupyter notebooks and video learning — watch, implement, explain

[Home](../README.md) · [Notebook index](../notebooks/README.md) · [Visual VS Code setup](VS-CODE-LEARNING-SETUP.md)

**This repository does not host, download or redistribute video courses.** It links to the original provider's material. Copyright belongs to the publisher under that publisher's terms.

## How to use the guided notebooks

1. Open the repository in VS Code with the **Jupyter extension**, or use JupyterLab in a dedicated virtual environment.
2. Open `.ipynb` files as **visual cells**, not raw JSON. Select a Python kernel and predict the output before running each exercise.
3. Some early notebooks use `IPython.display.YouTubeVideo` to embed a player where the browser and network allow it. **GitHub's static notebook preview may not show embedded iframes.** Direct video links are always available.
4. After one short relevant segment, implement a code task, reproduce an error and answer a transfer question. Watching a video does not count as completing the stage.
5. Without YouTube access, use official text documentation and the synthetic exercise; the learning path does not depend on video playback.

## The first four video-linked notebooks

| Notebook | Practice | Original educational source | CS connection |
| --- | --- | --- | --- |
| [00 — Data Journey](../notebooks/00_data_journey.ipynb) | End-to-end data flow | [DataTalks.Club — Orchestration](https://www.youtube.com/watch?v=-JLnp-iLins) | Provenance and types |
| [01 — SQL Detective](../notebooks/01_sql_detective.ipynb) | Joins and cardinality | [Harvard CS50 SQL](https://www.youtube.com/watch?v=WXk7yDqsKxs) | Relational algebra and indexes |
| [02 — ETL Failure Lab](../notebooks/02_etl_failure_lab.ipynb) | Replay and dedup | [dlt / ingestion workshop](https://www.youtube.com/watch?v=5eMytPBgmVs) | Invariants and idempotency |
| [03 — Pipeline Observatory](../notebooks/03_pipeline_observatory.ipynb) | Freshness and monitoring | [Workflow orchestration](https://www.youtube.com/watch?v=1pu_C_oOAMA) | SLIs and failure detection |

### Example original source

[![Harvard CS50 SQL — original course thumbnail](https://img.youtube.com/vi/WXk7yDqsKxs/hqdefault.jpg)](https://www.youtube.com/watch?v=WXk7yDqsKxs)

The linked source is a full SQL course. You do **not** have to watch it all before starting Notebook 01; focus on the actual gap shown by a diagnostic.

## Additional official learning resources

| Subject | Source | Best used near |
| --- | --- | --- |
| SQL fundamentals | https://cs50.harvard.edu/sql/ | Stage 01 |
| Terminal, Git and debugging | https://missing.csail.mit.edu/ | Stage 00 |
| Docker and infrastructure | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform | Stage 04 |
| Orchestration | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration | Stage 06 |
| Data warehousing | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse | Stage 05 |
| dbt | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering | Stage 05–07 |
| Spark | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch | Stage 10 |
| Kafka | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming | Stage 11 |

Prefer the **official course indexes** over copied, unverified video IDs: instructors can update links as training material changes.

## Notebook coverage: all 14 stages

Stages **04–13** have English guided notebooks with short synthetic Python examples and official source references instead of embedded videos. Run the self-contained advanced notebook examples with:

~~~bash
python3 scripts/notebook_smoke.py
~~~

These tutorials are **not** substitutes for the independent lab starters, real PostgreSQL/dbt/PySpark/Kafka runtime checks or a qualified capstone review.

## Mentor technique

Select one relevant learning segment. Before playback ask two prediction questions; afterward require a working code example, a counterexample the learner repairs and an explanation of **why** it works. Learners who already demonstrate the skill may skip the video and solve a harder unseen task.
