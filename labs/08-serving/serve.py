"""Run a bound-to-loopback training-only Data Serving dashboard.

Default mode creates a temporary, synthetic database that is removed on exit.
An optional --database PATH reads an existing Stage 07 SQLite DB in read-only mode.
"""
import argparse
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from demo import create_demo_database
from service import make_handler


def _run(db_path: Path, port: int):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(db_path))
    try:
        print("Training dashboard: http://127.0.0.1:" + str(server.server_port), flush=True)
        print("Only loopback; sample information is synthetic, not live or public.", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path,
                        help="Read an existing Stage 07 database; never modified")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    if args.database:
        if not args.database.is_file():
            parser.error("database file not found; no file created")
        _run(args.database, args.port)
    else:
        with TemporaryDirectory(prefix="dem-stage08-") as directory:
            db_path = Path(directory) / "synthetic.sqlite"
            create_demo_database(db_path)
            _run(db_path, args.port)


if __name__ == "__main__":
    main()

