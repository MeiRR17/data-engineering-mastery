
"""Safe operations incident drill: detect SLO breach, backup and restore.

All files live inside TemporaryDirectory and are deleted after completion.
Never modifies a real database, environment or secret.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from instructor.reference import (
    backup_database, compute_slo, create_synthetic_database, forecast_cost,
    restore_to_new, verify_backup,
)


def main():
    with TemporaryDirectory(prefix="dem-stage12-drill-") as folder:
        root=Path(folder)
        source=create_synthetic_database(root/"synthetic.sqlite")
        report=compute_slo(
            [{"window":"2026-01-02-01","status":"success"},
             {"window":"2026-01-02-02","status":"failed"},
             {"window":"2026-01-02-03","status":"blocked"}],
            [{"observed_at":"2025-12-31T22:00:00Z"}],
            datetime(2026,1,3,12,0,tzinfo=timezone.utc),
            {"target_availability":0.99,"max_freshness_hours":24,
             "max_blocked_fraction":0.1}
        )
        if report["passing"] or "FRESHNESS_STALE" not in report["issues"]:
            raise AssertionError("SLO incident was missed")
        backup,manifest=backup_database(source,root/"backup","before-incident")
        verified=verify_backup(backup,manifest)
        # This is a *synthetic incident* in the disposable source database only.
        with sqlite3.connect(source) as db:
            db.execute("delete from curated where event_id='synthetic-C'")
            db.commit()
        restored=root/"restored-safe-copy.sqlite"
        result=restore_to_new(backup,manifest,restored)
        with sqlite3.connect(restored) as db:
            final=db.execute("select count(*) from curated").fetchone()[0]
        if final!=3:
            raise AssertionError("restore did not reproduce original event count")
        cost=forecast_cost(
            events_per_day=20_000,bytes_per_event=1024,retention_days=30,
            price_per_gib_month=0.025,compute_hours=100,compute_rate=0.2
        )
        print(json.dumps({
            "result":"PASS","mode":"offline synthetic drill",
            "slo":report,"backup_rows":verified["rows"],
            "restore":result["status"],"restored_rows":final,
            "cost_scenario":cost,
            "caveat":"No remote restores, alerts, production RBAC or real vendor pricing tested."
        },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
