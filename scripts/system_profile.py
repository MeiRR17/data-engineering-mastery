#!/usr/bin/env python3
"""Privacy-preserving, opt-in local capacity hint; stdlib only, no network access."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "learner" / "system-profile.local.json"


def system_memory_gib() -> float | None:
    system = platform.system()
    try:
        if system == "Linux":
            lines = Path("/proc/meminfo").read_text(encoding="utf-8").splitlines()
            line = next(s for s in lines if s.startswith("MemTotal:"))
            return round(int(line.split()[1]) / 1024**2, 1)
        if system == "Darwin":
            r = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True,
                               text=True, check=True, timeout=3)
            return round(int(r.stdout.strip()) / 1024**3, 1)
        if system == "Windows":
            # No third-party package; memory status only, never serials or user info.
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            status = MEMORYSTATUSEX()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return round(status.ullTotalPhys / 1024**3, 1)
    except (OSError, ValueError, StopIteration, subprocess.SubprocessError, AttributeError):
        return None
    return None


def classify_tier(cores: int | None, memory_gib: float | None, disk_free_gib: float | None) -> str:
    """Conservative resource tiers, not a formal compatibility verdict."""
    if not cores or memory_gib is None or disk_free_gib is None:
        return "light"
    if cores < 2 or memory_gib < 8 or disk_free_gib < 10:
        return "light"
    if cores < 8 or memory_gib < 16 or disk_free_gib < 30:
        return "moderate"
    return "full"


def get_profile() -> dict:
    cpu = os.cpu_count()
    ram = system_memory_gib()
    try:
        disk = round(shutil.disk_usage(ROOT).free / 1024**3, 1)
    except OSError:
        disk = None
    tier = classify_tier(cpu, ram, disk)
    return {
        "schema_version": "1.0.0",
        "source": "local_opt_in",
        "os_family": platform.system(),  # no hostname, username, home path, IP or serial
        "architecture": platform.machine(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "logical_cpu_count": cpu,
        "ram_gib_approx": ram,
        "free_disk_gib_approx": disk,
        "git_cli_installed": shutil.which("git") is not None,
        "docker_cli_installed": shutil.which("docker") is not None,
        "resource_tier": tier,
        "tier_is_estimate": True,
        "recommended_environment": {
            "light": "SQLite / DuckDB / small fixtures; hosted tools only after consent and cost check",
            "moderate": "SQLite + PostgreSQL (Docker if daemon works); cloud optional",
            "full": "PostgreSQL; consider local Spark/Kafka later with resource caps",
        }[tier],
        "privacy_note": "Local only; do not commit this profile or share identifiers",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-local", action="store_true", help="Save gitignored local JSON, never upload")
    ap.add_argument("--tier-only", action="store_true", help="Print only light/moderate/full")
    args = ap.parse_args()
    profile = get_profile()
    if args.tier_only:
        print(profile["resource_tier"])
    else:
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    if args.write_local:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(OUT, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("Local, gitignored profile saved to learner/system-profile.local.json", file=sys.stderr)


if __name__ == "__main__":
    main()
