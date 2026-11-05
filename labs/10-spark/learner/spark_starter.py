"""Complete the Spark-native transformation, without using .collect() on input.

Input: a PySpark DataFrame with normalized columns:
event_id, observed_utc, updated_utc, region_code, magnitude (nullable), digest.
Return a Spark DataFrame with one row per (day_utc, region_code) and:
total_events, known_magnitude_events, average_magnitude.

Use repartition(), Window+row_number(), groupBy(), avg() and sorting.
The latest source_updated timestamp wins per ID; digest breaks equal-time ties.
"""
def build_mart(df, partitions=2):
    raise NotImplementedError("Implement Spark partitioning, dedup and grouped mart")

