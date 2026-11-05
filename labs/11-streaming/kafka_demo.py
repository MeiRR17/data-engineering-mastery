"""Real single-broker Kafka integration for Stage 11, synthetic topic only.

Requires optional confluent-kafka==2.16.1 and Apache Kafka 4.4.0.
Broker target is deliberately restricted to loopback to avoid modifying a
user's remote/production cluster. Creates an ephemeral topic with two
partitions, sends eight events, reads with explicit assignments, checkpoints
local SQLite then explicitly commits offsets to the Kafka broker.

WARNING: committing broker offsets is not atomic with the SQLite transaction.
This test demonstrates local idempotency/recovery, not cross-system EOS.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import time
import uuid

from instructor.reference import AckLost, consume, read_log, snapshot

LAB=Path(__file__).resolve().parent
BROKERS={"127.0.0.1:9092","localhost:9092"}


def run_demo(broker):
    if broker not in BROKERS:
        raise ValueError("only a local disposable Kafka broker is allowed")
    try:
        from confluent_kafka import (
            Producer,Consumer,TopicPartition,KafkaException
        )
        from confluent_kafka.admin import AdminClient,NewTopic
    except ImportError as exc:
        raise RuntimeError("Install confluent-kafka==2.16.1 for broker mode") from exc

    admin=AdminClient({"bootstrap.servers":broker,"socket.timeout.ms":2000,
                       "request.timeout.ms":5000})
    deadline=time.monotonic()+120
    while True:
        try:
            cluster=admin.list_topics(timeout=5)
            if cluster.brokers:
                break
        except KafkaException:
            pass
        if time.monotonic()>deadline:
            raise TimeoutError("local Kafka broker did not become ready")
        time.sleep(2)

    suffix=uuid.uuid4().hex[:12]
    topic="dem-stage11-"+suffix
    group="dem-stage11-"+suffix
    future=admin.create_topics([NewTopic(topic,num_partitions=2,replication_factor=1)])
    future[topic].result(timeout=30)

    sent=read_log(LAB/"data/synthetic_log.jsonl")
    errors=[]
    producer=Producer({
        "bootstrap.servers":broker,
        "enable.idempotence":True,
        "acks":"all",
        "message.timeout.ms":20000,
        "socket.timeout.ms":5000,
    })
    def delivered(err,_message):
        if err is not None:
            errors.append(str(err))
    for item in sent:
        producer.produce(
            topic=topic,partition=item["partition"],
            key=item["value"].get("event_id","invalid").encode("utf8"),
            value=json.dumps(item["value"]).encode("utf8"),
            on_delivery=delivered
        )
        producer.poll(0)
    pending=producer.flush(timeout=45)
    if pending or errors:
        raise RuntimeError("Kafka producer delivery failed or did not flush")

    consumer=Consumer({
        "bootstrap.servers":broker,
        "group.id":group,
        "auto.offset.reset":"earliest",
        "enable.auto.commit":False,
        "enable.auto.offset.store":False,
        "session.timeout.ms":15000
    })
    try:
        consumer.assign([TopicPartition(topic,0,0),TopicPartition(topic,1,0)])
        received=[]
        poll_end=time.monotonic()+75
        while len(received)<len(sent) and time.monotonic()<poll_end:
            message=consumer.poll(timeout=2)
            if message is None:
                continue
            if message.error():
                raise RuntimeError("Kafka consumer poll failed: "+str(message.error()))
            received.append({
                "partition":message.partition(),
                "offset":message.offset(),
                "value":json.loads(message.value().decode("utf8"))
            })
        if len(received)!=len(sent):
            raise RuntimeError(f"Kafka received {len(received)} of {len(sent)} events")

        with sqlite3.connect(":memory:") as db:
            try:
                consume(db,received,lose_ack=True)
            except AckLost:
                pass
            before=snapshot(db)
            # The broker and SQLite are distinct consistency boundaries.
            # Here we commit broker offsets AFTER the SQLite transaction.
            offsets=[
                TopicPartition(topic,item["partition"],item["next_offset"])
                for item in before["offsets"]
            ]
            consumer.commit(offsets=offsets,asynchronous=False)
            broker_offsets=consumer.committed(
                [TopicPartition(topic,0),TopicPartition(topic,1)],timeout=10
            )
            committed=sorted([{"partition":x.partition,"next_offset":x.offset}
                              for x in broker_offsets],key=lambda x:x["partition"])
            if committed!=before["offsets"]:
                raise RuntimeError("broker and local committed next offsets disagree")
            replay=consume(db,received)
            after=snapshot(db)
            if replay["status"]!="skipped" or after!=before or len(after["events"])!=4:
                raise RuntimeError("Kafka round-trip replay changed curated state")
            return {
                "result":"PASS",
                "broker_mode":"Apache Kafka single-broker, local-only",
                "delivered":len(sent),"received":len(received),
                "events":len(after["events"]),
                "dead_letters":len(after["dead_letters"]),
                "sqlite_next_offsets":before["offsets"],
                "broker_next_offsets":committed,
                "replay":replay["status"],
                "distributed_exactly_once_verified":False,
            }
    finally:
        consumer.close()
        # The entire broker container is ephemeral; deleting the topic here
        # is best effort, never a production cleanup command.
        try:
            admin.delete_topics([topic],operation_timeout=5)
        except Exception:
            pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--broker",default="127.0.0.1:9092")
    args=parser.parse_args()
    print(json.dumps(run_demo(args.broker),ensure_ascii=False,sort_keys=True,indent=2))


if __name__=="__main__":
    main()

