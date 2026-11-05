# Computer Science bridges for Data Engineers

The course links theory to **behavior visible in working software**. An algorithm matters because it explains a performance result; a transaction matters because it prevents partial data.

| Data Engineering example | Underlying CS | Experiment |
| --- | --- | --- |
| PostgreSQL indexes | B-trees, complexity, cache locality | Compare sequential and index scans with 10k/100k synthetic rows |
| Batch ingestion | Processes, I/O vs CPU bound work | Compare sequential and bounded concurrent requests |
| Upsert / transaction | ACID, locking, isolation | Inject a pre-commit failure and verify atomicity |
| API retries | HTTP, TCP, backoff and jitter | Simulate 429 and timeout |
| Data quality | Bias and false positives | Compare precision/recall of a proposed rule |
| SCD Type 2 | Time semantics and invariants | Correctly join a late event to its historical dimension |
| Orchestration | Graph theory and topological sorting | Detect a cycle before running a DAG |
| Kafka consumer | Ordering and delivery guarantees | Crash and replay a duplicated or delayed event |
| RLS / IAM | Least-privilege trust boundaries | Deny an unauthorized read/write |
| Spark | Parallelism, shuffle, Amdahl's law | Investigate overhead on a small local job |
| Parquet | Columnar encoding and compression | Compare size and projected-column access against JSON |
| SLO / recovery | Reliability math and failure domains | Compute error budget and run a safe restore |

## Complete theoretical foundation

- **Algorithms:** Big-O, maps, sorting, B-trees, graphs, heaps and external merge sort.
- **Operating systems:** processes/threads, virtual memory, page cache, file systems, permissions and scheduling.
- **Networks:** TCP/IP, DNS, TLS, HTTP, throughput, latency, retries and backpressure.
- **Databases:** relational algebra, ACID, MVCC, isolation, WAL and query optimization.
- **Statistics:** distributions, sampling, confidence, false positives, seasonality and anomaly detection.
- **Distributed systems:** partitions, replicas, ordering, idempotency, consensus fundamentals and consistency trade-offs.
- **Security:** access control, RLS, SQL injection, secrets, supply chain and threat modeling.
- **Software engineering:** test pyramid, maintainability, observability, profiling and CI.

Study **one focused bridge per week** tied to a current lab. If a diagnostic exposes a critical gap, finish that bridge before advancing. For short independent reading and practice, choose one of the eight [dedicated CS bridge units](../curriculum/cs-bridges/algorithms.md).
