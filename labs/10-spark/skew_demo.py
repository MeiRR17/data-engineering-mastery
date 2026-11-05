
"""Small PySpark Data Skew demonstration (no performance promises).

Partitioning by a low-cardinality hot region creates heavy skew.
Partitioning by a high-cardinality event ID is much more balanced.
Only uses synthetic local data; no services, data downloads, or cost.
"""
from __future__ import annotations
import json
from pyspark.sql import functions as F
from spark_pipeline import session


def counts_per_partition(df, partitions, key):
    counts = (df.repartition(partitions, F.col(key))
              .withColumn("partition_id", F.spark_partition_id())
              .groupBy("partition_id").count().collect())
    output = [0] * partitions
    for record in counts:
        output[record["partition_id"]] = record["count"]
    return output


def main():
    spark = session()
    try:
        # 900 events use HOT, 100 are distributed among three cold regions.
        synthetic = [(f"evt-{i:04d}", "HOT" if i < 900 else
                      ("E", "W", "S")[i % 3]) for i in range(1000)]
        data = spark.createDataFrame(synthetic, "event_id string, region_code string")
        by_region = counts_per_partition(data, 4, "region_code")
        by_id = counts_per_partition(data, 4, "event_id")
        if sum(by_region) != 1000 or sum(by_id) != 1000:
            raise AssertionError("partition accounting mismatch")
        if max(by_region) <= max(by_id):
            raise AssertionError("unexpected demo: region skew should be worse than ID partitioning")
        print(json.dumps({
            "result": "PASS", "mode": "synthetic Spark local[2]",
            "rows": 1000, "hot_region_rows": 900,
            "partition_by_region": by_region, "partition_by_event_id": by_id,
            "region_max_to_mean": round(max(by_region) / 250, 2),
            "event_id_max_to_mean": round(max(by_id) / 250, 2),
            "warning": "This demonstrates skew distribution, not that one job is faster."
        }, indent=2))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
