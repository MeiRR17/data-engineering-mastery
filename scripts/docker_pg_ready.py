"""Wait until the *final* official PostgreSQL container server has started.

The official postgres Docker entrypoint briefly starts a temporary server
during initdb and then stops it. pg_isready can report success during this
temporary phase; executing migration SQL at that moment is a race.
"""
from __future__ import annotations

import subprocess
import time

INITIALIZATION_FINISHED = "PostgreSQL init process complete; ready for start up."


def wait_for_final_postgres(container: str, *, attempts: int = 90,
                            runner=subprocess.run, sleeper=time.sleep) -> None:
    if not isinstance(container, str) or not container:
        raise ValueError("container name required")
    if not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be positive")
    for _ in range(attempts):
        logs = runner(["docker", "logs", container], capture_output=True,
                      text=True, check=False)
        log_text = (logs.stdout or "") + "\n" + (logs.stderr or "")
        if logs.returncode == 0 and INITIALIZATION_FINISHED in log_text:
            ready = runner(
                ["docker", "exec", container, "pg_isready",
                 "-U", "postgres", "-d", "learning"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False,
            )
            if ready.returncode == 0:
                return
        sleeper(1)
    raise RuntimeError(
        "PostgreSQL final server did not become ready after initdb; "
        "temporary startup readiness is not enough."
    )

