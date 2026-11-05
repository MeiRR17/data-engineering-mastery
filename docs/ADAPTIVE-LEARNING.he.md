# Adaptive Learning — personalize the exercise, not the facts

The mentor chooses the next small task based on **demonstrated skills and constraints**, not a degree, job title or unsupported assumptions. Adaptation must be opt-in and must never collect a learner's private information without permission.

## Inputs (only with learner consent)

- **Previous knowledge:** a short diagnostic, an independent transfer question and observed test results.
- **Goal:** first Data Engineering role, platform specialization, research or general skill development.
- **Time:** session minutes and realistic weekly practice capacity.
- **Hardware:** an *optional local* summary of CPU, RAM, available storage and Docker capability; no hostname, username, serial number or identifying inventory.
- **Learning evidence:** passed tests, recurring errors, number of hints required and the learner's own explanations.

## Choosing the next exercise

1. If a safety-critical knowledge gap blocks safe tool use, assign a small Computer Science bridge and a focused experiment.
2. Choose **one or two** concrete tasks from the current stage, not an entire backlog.
3. Use the optional resource classification: `light` = Python/SQLite; `moderate` = optional PostgreSQL/dbt/Docker; `full` = PySpark and single-node Kafka if justified.
4. Start with a curious failure: ask the learner to **predict** the output before running code.
5. Assess understanding on **a new input**, not by repeating the reference implementation.
6. When a topic requires three or more hints, schedule a short revision and revisit it later. Otherwise test retention in 7–14 days.
7. Offer at most one side quest of 15–25 minutes per session, and let the learner skip it if it is not blocking.

## Hardware-aware modes

| Mode | Suitable work | Defer or simplify |
| --- | --- | --- |
| Light | Python, CSV/JSON, SQLite, small fixtures, documentation | Full local Kafka/Spark and many containers |
| Moderate | PostgreSQL, Docker, dbt, optional local Supabase | Expensive multi-service clusters |
| Full | Local Spark and a single Kafka broker | Unapproved remote infrastructure or real production secrets |

Not being able to run Kafka locally does **not** imply a lack of conceptual understanding. Record full-mode hands-on practice as *not yet verified* until a real approved environment becomes available.

## Session formats

- **Incident detective:** hypothesis → safe experiment → conclusion → regression.
- **Build a feature:** add one capability under a data contract.
- **CS microscope:** investigate OS, network or algorithm-level behavior.
- **Peer review simulation:** defend design decisions and respond to review feedback.
- **Black-box challenge:** locate why invalid data escaped a quality gate.
- **Trade-off duel:** compare two designs on latency, cost, security and recovery.

## Example: Stage 03

**Hook:** Why did one synthetic earthquake event appear three times in analytics?  
**Prediction:** Retries may be writing duplicate business IDs or using the wrong unique key.  
**Experiment:** Run the ETL twice on the same fixture and compare counts and revisions.  
**CS bridge:** Idempotency and distributed retry semantics.  
**Transfer:** What if a server crashes after committing data but before sending the acknowledgement?  
**Exit question:** How would you repair the sink without erasing all historical source data?

The learner should end each session with a concrete next action and one piece of **sanitized evidence**, not a generic confidence score.
