# Optional Stage 07 transfer project — offline CSV schema drift audit

This is a **separate, runnable data-engineering exercise** that does not modify the course's existing Stage 07 learner starter, instructor oracle, graded scenarios or production integrations. It teaches why an apparently successful ETL run can publish incompatible CSVs and why an inferred schema is not a verified data contract.

The tool in [drift.py](drift.py) compares **two local CSV files** (baseline and candidate). It is Python 3.11+ standard-library only: no credentials, HTTP calls, cloud resources, databases, personal information, SDK installations or writes to the input files. Both inputs are fully scanned within bounded size limits. Results go to standard output; no files are saved automatically.

## Run with the bundled synthetic fixtures

From the repository root:

```bash
# Candidate has a newly added source_batch column and 25% missing magnitudes.
# This is a warning under the default rules; returns 0 unless --fail-on-warning.
python3 examples/schema-drift-audit/drift.py \
  --baseline examples/schema-drift-audit/data/baseline.csv \
  --candidate examples/schema-drift-audit/data/candidate-warning.csv

# Use a stricter gate and machine-readable aggregate output.
python3 examples/schema-drift-audit/drift.py \
  --baseline examples/schema-drift-audit/data/baseline.csv \
  --candidate examples/schema-drift-audit/data/candidate-warning.csv \
  --format json --fail-on-warning

# Breaking candidate removes quality_band and introduces incompatible values.
python3 examples/schema-drift-audit/drift.py \
  --baseline examples/schema-drift-audit/data/baseline.csv \
  --candidate examples/schema-drift-audit/data/candidate-breaking.csv
```

The first input represents **invented events**, not real earthquake readings, people, production incidents or observed pipeline performance. None of these commands contacts the network.

## Audited fields and compatibility rules

The scanner collects, per column, a **row count, missing-value count, missing fraction, inferred scalar kind and count by detected kind**. It never prints cell values or records from the source. A blank or whitespace-only cell is missing; the literal string `null` is ordinary text unless the user preprocesses it under an explicitly documented contract.

Inferred kinds: `boolean` (true/false only), `integer` (canonical signed decimal), `decimal` (finite decimal/scientific numbers), ISO `date`, ISO `timestamp`, `text`, `empty` (no nonempty values) and `mixed` (more than one incompatible kind). Integer + decimal values are treated as `decimal`. Inference never converts a source cell or guesses a type from a column name.

The comparison emits findings using three severities:

| Change | Default classification |
| --- | --- |
| Baseline column removed | Breaking |
| Inferred type changes to another unambiguous, incompatible type | Breaking |
| Additional column | Warning (breaking with `--strict-additions`) |
| Original integer inferred as decimal | Informational widening |
| Mixed or empty kind change | Warning, because evidence is insufficient |
| Missing fraction rises by **more than** 0.10 | Warning; configure `--max-missing-increase` |
| Existing columns appear in different relative order | Warning |
| No findings | Compatible **under these narrow rules** |

These rules are deliberately conservative and do **not** establish the correctness of values or downstream SQL. For instance, if dates are represented as text in both datasets, changes in their business meaning will not be detected.

## Exit codes and failure boundaries

| Exit code | Meaning |
| --- | --- |
| 0 | No breaking change under these rules; warnings permitted by default |
| 1 | Breaking change, or warning when `--fail-on-warning` is set |
| 2 | Invalid CLI arguments or rejected input (the audit result is incomplete) |

Limits: each source must be a regular file (not a symbolic link), at most **20 MiB**, with at most **100,000 data rows**, **100 columns**, and **256 KiB per field**. Input must be UTF-8 or UTF-8 with BOM. Empty data files, blank/duplicate headers, malformed CSV quoting, malformed UTF-8, and ragged rows are rejected instead of silently ignored. No partial result is published when an input cannot be parsed.

The `--format json` report contains column names and aggregate counts, not raw records or sampled values. A column **name itself** may still be sensitive, so use this tool only on sources you are authorized to inspect and protect any saved output. Avoid checking private data into Git or sending reports to remote services. Programmatic consumers should interpret `schema_version: 1` and `status` rather than parsing free-form Markdown.

## Independent transfer challenge

Without reading the implementation, predict which checks should block publication if:

1. A source suddenly starts emitting `magnitude=unknown`.
2. The event ID becomes nullable but the field is still called `event_id`.
3. A producer reorders column positions while keeping the exact names.
4. The candidate contains the original columns plus a new optional column.
5. The data remain syntactically identical but were collected from an unlicensed source.

Explain why schema inference alone cannot prove provenance, quality, privacy, freshness or a learner's competence. A production contract should use **explicit schema versions, accepted null policies, unique keys, domain constraints, provenance and consumer agreements**, not just this audit.

**Status:** a feature-branch code-only teaching addition. No commands, CI, tests, network requests or data processing were executed in this development cycle. Its result is not validated until owner-run acceptance.
