"""Run Stage 04 on a temporary Docker PostgreSQL instance (no ports/volumes)."""
import argparse
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from docker_pg_ready import wait_for_final_postgres

def run(*args, quiet=False):
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.DEVNULL if quiet else None)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true", help="Run instructor solution for CI")
    parser.add_argument("--answers", type=Path, help="Own SQL file; omit to use starter.sql")
    args = parser.parse_args()
    if args.reference and args.answers:
        parser.error("Choose --reference or --answers, not both")
    answers = (LAB / "instructor/reference.sql" if args.reference else
               (args.answers or LAB / "starter.sql")).resolve()
    if not answers.is_file():
        parser.error("Missing answers file: " + str(answers))
    if shutil.which("docker") is None:
        print("Docker unavailable; see lab README for alternative", file=sys.stderr)
        return 2
    name = "de-mastery-stage04-" + uuid.uuid4().hex[:12]
    started = False
    try:
        run("docker", "run", "-d", "--rm", "--name", name,
            "-e", "POSTGRES_PASSWORD=disposable-only",
            "-e", "POSTGRES_DB=learning", "postgres:17", quiet=True)
        started = True
        # Wait beyond the entrypoint's temporary initdb PostgreSQL server.
        wait_for_final_postgres(name)

        sources = [
            LAB / "bootstrap.sql",
            ROOT / "projects/datapulse/database/001_init.sql",
            LAB / "seed.sql", answers, LAB / "tests/checks.sql"
        ]
        for i, source in enumerate(sources):
            destination = "/tmp/stage04_" + str(i) + ".sql"
            run("docker", "cp", str(source), name + ":" + destination, quiet=True)
            run("docker", "exec", name, "psql", "-X", "-v", "ON_ERROR_STOP=1",
                "-U", "postgres", "-d", "learning", "-f", destination, quiet=True)
        print("PASS: PostgreSQL migration, RLS, RPC, replay, rollback and analytics.")
        return 0
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    finally:
        if started:
            subprocess.run(["docker", "rm", "-f", name], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    raise SystemExit(main())
