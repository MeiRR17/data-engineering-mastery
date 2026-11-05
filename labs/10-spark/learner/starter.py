
"""Stage 10 learner starter. Implement the same contract without copying the oracle.

Use only Python standard library. The grader invokes run_light(path, partitions).
Don't use Spark here: this is the light fallback for all machines. The PySpark
challenge is a separate extension with a real Spark DataFrame job.
"""
def run_light(path, partitions=2):
    """Map/reduce with stable partitioning, latest-update dedup and UTC metrics.

    Return:
      input_rows, valid_rows, rejected_rows, rejected_reasons (sorted),
      deduplicated_events, duplicates_removed,
      metrics (sorted list of day_utc, region_code, total_events,
               known_magnitude_events, average_magnitude).
    Bad records are not published; record reason codes only.
    """
    raise NotImplementedError("Implement the Stage 10 partitioned aggregation lab")
