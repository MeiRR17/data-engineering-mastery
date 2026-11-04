"""Stage 05: real PostgreSQL star schema + SCD2, in a disposable Docker container.

No ports, volumes, local secrets, or remote services. Exit status determines pass.
"""
import argparse
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(__file__).resolve().parent
STAGE04 = ROOT / "labs/04-postgres"
SCHEMA = ROOT / "projects/datapulse/database/001_init.sql"


def run(*args, quiet=False):
    return subprocess.run(
        args, check=True, text=True,
        stdout=subprocess.DEVNULL if quiet else None,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true", help="Run instructor solution (CI)")
    parser.add_argument("--answers", type=Path, help="Own SQL file; default starter.sql")
    args = parser.parse_args()
    if args.reference and args.answers:
        parser.error("Choose --reference or --answers")
    answer = (LAB / "instructor/reference.sql" if args.reference else
              (args.answers or LAB / "starter.sql")).resolve()
    if not answer.is_file():
        parser.error("Answer file does not exist")
    if shutil.which("docker") is None:
        print("Docker is required for this real-PostgreSQL exercise.", file=sys.stderr)
        return 2

    name = "de-mastery-stage05-" + uuid.uuid4().hex[:12]
    started = False

    def psql_file(path, number):
        remote = "/tmp/stage05_" + str(number) + ".sql"
        run("docker", "cp", str(path), name + ":" + remote, quiet=True)
        run("docker", "exec", name, "psql", "-X", "-v", "ON_ERROR_STOP=1",
            "-U", "postgres", "-d", "learning", "-f", remote, quiet=True)

    try:
        run("docker", "run", "--rm", "-d", "--name", name,
            "-e", "POSTGRES_PASSWORD=disposable-only",
            "-e", "POSTGRES_DB=learning", "postgres:17", quiet=True)
        started = True
        for _ in range(45):
            ready = subprocess.run(
                ["docker", "exec", name, "pg_isready", "-U", "postgres", "-d", "learning"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Temporary PostgreSQL did not start")

        # A real exercise starts with a fresh database, not a shared cloud DB.
        steps = [
            ("roles", STAGE04 / "bootstrap.sql"),
            ("schema", SCHEMA),
            ("fixture", STAGE04 / "seed.sql"),
            ("model setup", LAB / "setup.sql"),
            ("learner model", answer),
            ("quality and SCD2", LAB / "tests/checks.sql"),
            ("idempotent replay", answer),
            ("replay verification", LAB / "tests/checks.sql"),
            ("synthetic correction", LAB / "tests/source_update.sql"),
            ("incremental refresh", answer),
            ("late correction verification", LAB / "tests/replay.sql"),
        ]
        for index, (label, path) in enumerate(steps):
            print("Stage 05:", label, flush=True)
            psql_file(path, index)
        print("PASS: Stage 05 star schema, historical SCD2, metrics, idempotency and refresh.")
        return 0
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print("FAIL: Stage 05 PostgreSQL lab: " + str(error), file=sys.stderr)
        return 1
    finally:
        if started:
            # Only the container created here is removed. No global docker cleanup.
            subprocess.run(
                ["docker", "rm", "-f", name], check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    raise SystemExit(main())

