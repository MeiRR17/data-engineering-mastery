# Stage 02 — Python Data Contract and Fault-Tolerant Parsing

[Back to foundations](../../docs/FOUNDATIONS-LABS.he.md) · [Stage 02](../../curriculum/modules/02.md)

## What happened?
A GeoJSON event feed returns three perfectly normal records, and tomorrow it returns a string instead of a number, a boolean timestamp, a missing coordinate and an invalid latitude. The pipeline must not silently corrupt downstream analytics.

Your code lives in **`labs/02-python/starter.py`**. No cloud account, pip install, API key or external network call is required.

```bash
python3 labs/02-python/grade.py
```

Initial failure is intentional. The CI checks the independent reference implementation using `--reference`; your personal `starter.py` remains your work.

## Contract
Implement two functions: `normalize_feature(feature)` and `clean_batch(features)`.

`normalize_feature` expects one GeoJSON `Feature` with `properties.type='earthquake'`, `geometry.type='Point'`, three numeric coordinates `[longitude, latitude, depth]`, `id`, `time`, `updated`, optional magnitude (`mag`), optional place (`place`). Return:

```python
{
    "event_id": "demo-a1",
    "observed_at": "2026-11-02T...+00:00",    # ISO UTC, from epoch milliseconds
    "source_updated_at": "2026-11-02T...+00:00",
    "magnitude": 4.6,                    # or None
    "longitude": -122.2,
    "latitude": 38.2,
    "depth_km": 8.1,
    "place": "Demo: Northern Region"
}
```

Rules: event ID matches `[A-Za-z0-9_-]{1,64}`; `time/updated` are finite numbers in *milliseconds*, never booleans; `updated >= time`; lat in `[-90,90]`, lon in `[-180,180]`, depth in `[-50,1000]`, magnitude in `[-5,12]` or `None`; strings are not coerced into numeric values. Unknown or empty place becomes `Unknown`, limited to 300 characters. Do not mutate input.

`clean_batch(features)` takes a list of features and returns `{"valid": [...], "rejected": [{"index": 0, "reason": "..."}]}`. Reject bad rows individually, preserving input indices. Never include the raw source row in the error message (privacy/logging).

## Learning sequence
1. Read `projects/datapulse/data/sample.geojson` and sketch the nested shape.
2. Implement smallest valid event, then write `ValidationError(ValueError)` for a bad field.
3. Check boundaries and `float('nan')`, `bool` versus `int`, missing nested objects, timestamp handling and no input mutation.
4. Implement batch isolation so one invalid row cannot block every valid row.
5. Run `grade.py`, reproduce one failure yourself and explain why it occurs.
6. CS side quest: why is streaming with an iterator useful when the file cannot fit in RAM?

## Exit gate
6 grading cases pass, plus 2 new edge cases you design yourself. Explain exception taxonomy, memory complexity and why timestamp timezone needs explicit normalization. Write an independent validator from a different API payload without copying the solution.

The instructor reference (`instructor/reference.py`) is for maintainer CI and may be inspected *after* your own attempt.
