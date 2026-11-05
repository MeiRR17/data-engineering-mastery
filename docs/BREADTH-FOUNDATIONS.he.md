# Foundations Passport — broad technical confidence

[Home](../README.md) · [Roadmap](ROADMAP.he.md) · [Mastery matrix](MASTERY-MATRIX.he.md)

Data Engineering depends on more than memorizing pipeline tools. Software engineers need enough **computer science and adjacent-domain breadth** to reason with backend, SRE, security, analytics, product and AI teams.

The strategy is **professional depth in Data Engineering + evidence of breadth in related disciplines**. It is not twelve simultaneous courses, a second university degree or a claim that watching a video is the same as building software.

~~~mermaid
flowchart TD
  A[Data Engineering question] --> B[Build a working example]
  B --> C[Explore a related CS concept]
  C --> D[Predict the behavior]
  D --> E[Test with synthetic data]
  E --> F[Explain without AI]
  F --> G[Apply to a new problem]
  G --> H[Record safe evidence and the next step]
~~~

## How to fit breadth into a focused curriculum

For a 10-hour study week, a practical default is seven hours of Data Engineering, two hours of adjacent Computer Science and one hour of revision and no-AI transfer practice. For five hours, use approximately 3.5 / 1 / 0.5. These are planning ratios, **not automatic promotion criteria**.

Each stage has an optional quest. A quest becomes required only when an assessed knowledge gap blocks safe or correct work. Missing hardware is a reason to use a simulation, not to claim full hands-on competence.

## The 12-domain passport

| Domain | Why it matters | Suggested stage |
| --- | --- | --- |
| Hardware and operating systems | Memory, disk, processes and CPU vs I/O | 00 |
| Algorithms and data structures | Indexes, complexity and query planning | 01 |
| Software engineering and testing | Contracts, regression, debugging | 02 |
| Networks and HTTP | API failures, timeouts, retries, backpressure | 03 |
| Information security | IAM, RLS, keys and least privilege | 04 |
| Mathematics and statistics | Bias, metrics and quality thresholds | 05/07 |
| Graphs and scheduling | DAG dependencies and failure domains | 06 |
| Ethics and data governance | Licensing, provenance, privacy, retention | 07/12 |
| Product and analytics UX | Metric definitions, stakeholder questions | 08 |
| Cloud economics and FinOps | Costs, trade-offs and ongoing operations | 09 |
| Distributed systems | Event order, replay and delivery semantics | 10/11 |
| AI literacy and communication | Source verification and case-study writing | 13 |

After the capstone, learners may explore robotics, embedded development, computer vision, mobile apps or cloud security independently. Those are **electives**, not hidden Data Engineering graduation gates.

## Use the offline quest explorer

~~~bash
python3 scripts/breadth_quest.py list
python3 scripts/breadth_quest.py recommend --stage 03
python3 scripts/breadth_quest.py show Q04
python3 scripts/breadth_quest.py check
~~~

The explorer reads [12 structured breadth quests](../curriculum/breadth-quests.json). It does not inspect hardware, call a cloud service, upload telemetry or modify private progress.

## A 30–45-minute quest protocol

1. **Predict:** write an expected outcome and a reason.
2. **Experiment:** use a small synthetic input or a safe simulation.
3. **Record:** preserve commands, expected versus observed results, tool version and redacted logs.
4. **Explain:** identify assumptions, the root cause and a plausible failure mode.
5. **Transfer:** solve a related but different challenge without AI hints.
6. **Evidence:** describe what you can independently perform, not how confident you feel.

### Self-assessment scale

| Level | Meaning |
| --- | --- |
| 0 | Not yet familiar with the concept |
| 1 | Can explain it in plain language |
| 2 | Can complete a guided experiment |
| 3 | Can debug and explain a new case independently |
| 4 | Can transfer the insight to another problem and justify trade-offs |

A score reflects **demonstrated skill at a particular task**, not a person's identity or worth. Explicitly recording "not yet understood" makes the next learning action more accurate.

## Evidence template

~~~text
Question and prediction:
Hardware mode (light/moderate/full, only if relevant):
Experiment or simulation:
Exact command and expected result:
Observed result:
Root cause and assumptions:
What surprised me:
New problem solved independently:
Safe evidence (file or personal PR):
Next review date (approximately 7–14 days):
~~~

## Mentor responsibilities

Start with one question rather than a long lecture; offer graduated hints; check **predictions before execution**; keep confidence separate from passing evidence; recommend videos only when useful; never label someone an expert after one lab or a fixed number of hours; request consent before costly or sensitive operations.

Further official learning resources: [MIT Missing Semester](https://missing.csail.mit.edu/), [Python](https://docs.python.org/3/tutorial/), [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP), [PostgreSQL](https://www.postgresql.org/docs/), [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/).
