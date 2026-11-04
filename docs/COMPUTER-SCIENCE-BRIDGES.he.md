# להרחיב מדעי המחשב מתוך עולם הנתונים

המטרה היא ללמוד מדעי המחשב בדרך **סמויה אך משמעותית**: כל נושא תיאורטי מסביר התנהגות שהלומד רואה באפליקציה שפיתח.

| Data Engineering | CS עמוק יותר | ניסוי מעניין |
|---|---|---|
| Index ב-PostgreSQL | B-Tree, סיבוכיות, Cache locality | השווה sequential scan ל-index scan עם 10k/100k rows |
| Batch ingestion | Processes, IO-bound vs CPU-bound, scheduling | בדוק זמן עם בקשות רצופות מול Concurrent (עם Rate Limit) |
| Upsert / Transaction | ACID, locks, isolation levels | הזרק תקלה באמצע טרנזקציה ובדוק Atomicity |
| API Retries | HTTP, TCP, exponential backoff, jitter | סימולציית 429 ו-timeout, בדיקת עומס |
| Data Quality | הסתברות, sampling bias, false positives | השווה Precision/Recall של חוק חריגות |
| SCD Type 2 | Time semantics, invariants | עדכן נתון היסטורי ובדוק שאילתה as-of |
| Orchestration DAG | Graph theory, topological order | בנה DAG עם cycle ונתח את הכשל |
| Kafka consumer | Distributed systems, ordering, exactly-once caveats | crash + replay, duplicate and late event |
| RLS / IAM | Security boundaries, least privilege | נסה unauthorized read/write עם public key |
| Spark | Parallelism, network shuffle, Amdahl's law | השווה overhead מול DuckDB בעומס קטן |
| Parquet | Compression, columnar data locality | השווה נפח/קריאת עמודות JSON מול Parquet |
| SLO and recovery | Reliability math, failure domains | חשב error budget ועשה restore drill |

## הסילבוס המלא להשגת בסיס מדעי המחשב

- אלגוריתמים ומבני נתונים: Big-O, hash maps, sorting, B-Trees, graphs, heaps, external merge sort.
- מערכות הפעלה: process/thread, virtual memory, file systems, page cache, scheduling, permissions.
- רשתות: TCP/IP, DNS, TLS, HTTP, latency, throughput, retries, backpressure.
- בסיסי נתונים: relational algebra, ACID, MVCC, isolation, indexes, execution plans, WAL.
- הסתברות וסטטיסטיקה: distributions, confidence, sampling, false positives, seasonality, anomalies.
- מערכות מבוזרות: CAP as a tradeoff model, partitions, replicas, ordering, idempotency, consensus basics.
- אבטחה: access control, RLS, SQL injection, secrets, supply chain, threat models.
- הנדסת תוכנה: SOLID במידה, test pyramid, CI, profiling, observability, maintainability.

הקצב: שיעור ממוקד אחד בשבוע + משימת ניסוי מתוך אחד הפרויקטים, במקום קורס מדעי המחשב במקביל בהיקף מלא. אם אבחון גילה פער קריטי, הופכים את ה-bridge לחובה לפני מעבר שלב.
