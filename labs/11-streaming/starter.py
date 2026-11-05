"""Stage 11 learner contract: implement a safe stream processor.

Do NOT copy instructor code. Run grade.py without --reference after your work.
Events include partition+offset envelopes and a JSON value. Implement durable
SQLite sink and offsets in the SAME transaction, idempotent replay, late-data
watermark and safe dead-letter reason codes. No broker required here.
"""
class AckLost(RuntimeError):
    pass


def ensure_schema(db):
    raise NotImplementedError("Create events, consumer_offsets, dead_letters")


def consume(db,messages,*,group_id="classroom",topic="synthetic-events",
            allowed_lateness_minutes=90,max_records=1000,
            crash_before_commit=False,lose_ack=False):
    raise NotImplementedError("Implement transactional consume/checkpoint")


def snapshot(db):
    raise NotImplementedError("Return safe events, offset and DLQ projection")

