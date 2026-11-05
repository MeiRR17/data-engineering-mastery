# Stage 11 — Kafka, Streaming Delivery & Exactly-once Caveats

[Stage 11 syllabus](../../curriculum/modules/11.md) · [Stage 10](../10-spark/README.md) · [Assessment](../../docs/ASSESSMENT.md)

**Goal:** understand how events arrive through a partitioned stream, how to checkpoint consumer offsets, how to tolerate duplicate delivery, and why “exactly once” depends on the boundaries of the system.

This stage has two levels. **Light mode** needs only Python + SQLite; **broker mode** uses a real local Apache Kafka broker and a Python producer/consumer. Both operate on synthetic, non-personal fixture data.

~~~mermaid
flowchart LR
  P[Producer] --> T[Topic partition log]
  T --> C[Consumer read from next offset]
  C --> W[Event-time watermark]
  W -->|late / invalid| D[Safe reason-only DLQ]
  W -->|valid| S[(Idempotent SQLite sink)]
  S --> O[(Consumer next-offset checkpoints)]
  O -->|restart| C
~~~

## Quickstart — no downloads or Docker

~~~bash
python3 labs/11-streaming/grade.py --reference
python3 labs/11-streaming/demo.py
# Student exercise; expected initial failures:
python3 labs/11-streaming/grade.py
~~~

The 25 reference tests cover partition offsets, out-of-order source revisions, replay, a crashed consumer *before* commit, a lost acknowledgement *after* commit, poison-pill quarantine, watermark lateness, bounds, immutable envelope identity, tie breaking and simulated rebalance/restart.

The learner implements the unfinished [starter.py](starter.py) using an independent method, then provides one extra unseen transfer scenario and a sanitized red-to-green test log.

### Streaming semantics demonstrated

- **Kafka-like topic partition/offset**: messages have a partition and increasing numeric offset. A checkpoint stores the next offset to consume. Never use an event ID as the Kafka offset.
- **Idempotent sink**: the primary key is event ID; a higher source revision can update it, an older revision cannot overwrite it. A deterministic content hash breaks equal-time conflicts in the educational fixture.
- **Transactional checkpoint**: each SQLite batch writes both curated records and the next consumer offsets in one transaction. A process crash before commit leaves neither. Lost client acknowledgement after commit causes replay to skip processed offsets.
- **At-least-once input vs local exactly-once effects**: Kafka can redeliver a message. This demo aims for an idempotent local state result, **not** distributed exactly-once transactions between Kafka and arbitrary sinks.
- **Watermark**: for this deterministic batch, max valid event time minus 90 minutes. Events older than that watermark are quarantined. This is a **batch teaching approximation**, not a production continuous watermark with per-partition idle detection.
- **DLQ/quarantine**: only partition, offset, reason code and consumer group are retained. Rejected raw payloads and secrets are deliberately excluded.
- **Rebalance**: consumer ownership can move to another worker, which must resume from the persisted checkpoint. This lab models restart semantics; real Kafka rebalance callbacks require separate practice.

## Real Kafka mode (optional, local machine with Docker)

Official quickstart and Docker image instructions: [Apache Kafka quickstart](https://kafka.apache.org/quickstart/) and [Docker](https://kafka.apache.org/44/getting-started/docker/). Kafka 4.4.0 requires Java 17+ when installed directly; Docker includes its runtime. Python client reference: [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/).

~~~bash
# Local disposable Kafka broker, loopback port only; no cloud or remote host:
docker run -d --rm --name dem-stage11-kafka -p 127.0.0.1:9092:9092 apache/kafka:4.4.0
python3 -m pip install "confluent-kafka==2.16.1"
# After the broker reports ready, run the full real producer/consumer exercise:
python3 labs/11-streaming/kafka_demo.py --broker 127.0.0.1:9092
# When finished:
docker rm -f dem-stage11-kafka
~~~

The optional Kafka step needs a running broker and available local memory. Do **not** use a shared/production Kafka cluster: the lab creates its own synthetic topic and test consumer group. Running the Docker command downloads a large image; low-memory learners should complete Light mode first.

## Learner tasks

1. Implement `ensure_schema`, `consume` and `snapshot` without looking at the reference first. Pass all 25 tests.
2. Explain why a downstream database transaction and Kafka's broker offsets live in different transactional systems.
3. Inject a crash before and after SQLite commit. Predict whether replay will write a duplicate, then prove it.
4. Change the lateness bound so a previously accepted record becomes late; explain business impact of dropping it.
5. Design an alternative policy: route late events to a correction topic rather than discarding them. Describe retention and compensation risks.
6. Sketch the consumer group rebalance process, static membership and how a partition moves between workers.
7. In broker mode, produce eight synthetic events and consume them using explicit Kafka partitions. Validate same curated state as the Light demo.
8. Explain tradeoffs between **Kafka, a polling ETL API and a daily batch**, including throughput, operational cost, complexity and failure recovery.

**Exit gate:** 25 local tests on student-owned code, a correction/replay case not in the grader, an incident explanation without AI, and **Kafka broker evidence** if claiming to have mastered Kafka itself. A Light-mode pass alone demonstrates streaming semantics but not broker operations.

**Not yet covered:** schema registry, Kafka Connect, KRaft cluster faults, multi-node throughput, exactly-once Kafka transactions, stateful Flink, full production monitoring and RBAC. These require separate advanced work beyond the single-broker exercise.

