"""Stage 13 capstone learner: integrate previous stages without copying the oracle.

Implement run_pipeline(workspace, *, inject_bad_batch=True,
                       crash_before_stream_commit=False).

You must build in a NEW workspace and output evidence.json with:
mode, overall_status, stream, data_quality, analytics, recovery,
release, claims. Never write into the original repository's training data.
"""
def run_pipeline(workspace,*,inject_bad_batch=True,
                 crash_before_stream_commit=False):
    raise NotImplementedError("Orchestrate Stage 11, 07, 08, 09 and backup/restore")

