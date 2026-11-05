"""Real PySpark local-mode DataFrame job for Stage 10.

Runs with Java 17 and pyspark==4.0.5. Data is validated/normalized in Python
first (teaching scope), then **deduplicated and aggregated in Spark** using a
window, repartition, groupBy and a shuffle. No cloud, Kafka or cluster.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from instructor.reference import check_partitions, read_jsonl, run_light


LAB = Path(__file__).resolve().parent


def session():
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise RuntimeError("PySpark is not installed; see Stage 10 README") from exc
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("DataEngineeringMastery-Stage10")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def normalized_dataframe(spark, records):
    from pyspark.sql.types import (
        DoubleType, StringType, StructField, StructType,
    )
    schema = StructType([
        StructField("event_id", StringType(), False),
        StructField("observed_utc", StringType(), False),
        StructField("updated_utc", StringType(), False),
        StructField("region_code", StringType(), False),
        StructField("magnitude", DoubleType(), True),
        StructField("digest", StringType(), False),
    ])
    return spark.createDataFrame([
        (r["event_id"], r["observed_utc"], r["updated_utc"],
         r["region_code"], r["magnitude"], r["digest"])
        for r in records
    ], schema=schema)


def build_mart(df, partitions=2):
    """Spark-native as-of dedup and grouped mart. Returns a Spark DataFrame."""
    from pyspark.sql import Window, functions as F
    check_partitions(partitions)
    # All revisions of an ID must converge on one partition before row_number.
    keyed = df.repartition(partitions, F.col("event_id"))
    ranked = keyed.withColumn(
        "_rank",
        F.row_number().over(
            Window.partitionBy("event_id")
            .orderBy(F.col("updated_utc").desc(), F.col("digest").desc())
        ),
    )
    latest = ranked.filter(F.col("_rank") == 1).drop("_rank")
    with_day = latest.withColumn("day_utc", F.substring(F.col("observed_utc"), 1, 10))
    return with_day.groupBy("day_utc", "region_code").agg(
        F.count(F.lit(1)).alias("total_events"),
        F.count(F.col("magnitude")).alias("known_magnitude_events"),
        F.round(F.avg(F.col("magnitude")), 2).alias("average_magnitude"),
    ).orderBy("day_utc", "region_code")


def result_rows(frame):
    return [
        {
            "day_utc": r.day_utc,
            "region_code": r.region_code,
            "total_events": int(r.total_events),
            "known_magnitude_events": int(r.known_magnitude_events),
            "average_magnitude": (
                float(r.average_magnitude) if r.average_magnitude is not None else None
            ),
        }
        for r in frame.collect()
    ]


def run_spark(path: Path, partitions=2, *, spark=None, explain=False):
    """Return a normalized report with Spark results and safe validation counters."""
    check_partitions(partitions)
    accepted, rejected = read_jsonl(path)
    owns = spark is None
    if spark is None:
        spark = session()
    try:
        df = normalized_dataframe(spark, accepted)
        mart = build_mart(df, partitions)
        if explain:
            mart.explain(mode="formatted")
        metrics = result_rows(mart)
        # This tiny educational fixture can be collected safely.
        # Real data jobs must write distributed results and never collect full datasets.
        return {
            "input_rows": len(accepted) + len(rejected),
            "valid_rows": len(accepted),
            "rejected_rows": len(rejected),
            "rejected_reasons": sorted(r["reason"] for r in rejected),
            "deduplicated_events": sum(x["total_events"] for x in metrics),
            "duplicates_removed": len(accepted) - sum(x["total_events"] for x in metrics),
            "metrics": metrics,
        }
    finally:
        if owns:
            spark.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=LAB / "data/synthetic_events.jsonl")
    parser.add_argument("--partitions", type=int, default=2)
    parser.add_argument("--explain", action="store_true",
                        help="Show the Spark execution plan including exchanges")
    args = parser.parse_args()
    actual = run_spark(args.input, args.partitions, explain=args.explain)
    expected = run_light(args.input, args.partitions)
    if actual != expected:
        print(json.dumps({"result": "FAIL", "spark": actual, "light": expected},
                         sort_keys=True, indent=2))
        raise SystemExit(1)
    print(json.dumps({"result": "PASS", "spark_version": "local-mode",
                      "partition_count": args.partitions, "report": actual},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

