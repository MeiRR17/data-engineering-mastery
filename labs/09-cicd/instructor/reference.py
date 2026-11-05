"""Stage 09 reference: deterministic bundles and safe local release promotion.

This is a learning simulator, NOT a real deployment driver. No network access,
subprocess calls, host service changes, credentials or production state.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

VERSION = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")
DIGEST = re.compile(r"[0-9a-f]{64}")
ENVIRONMENTS = {"dev", "staging", "prod-sim"}
STAMP = (1980, 1, 1, 0, 0, 0)


def _json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, prefix=".stage09-", delete=False) as f:
        temp = Path(f.name)
        try:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            temp.unlink(missing_ok=True)
            raise
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _version(value):
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError("version must be vN.N.N")


def _env(root, environment):
    if environment not in ENVIRONMENTS:
        raise ValueError("unknown simulated environment")
    root = Path(root)
    base = root / environment
    if any(p.is_symlink() for p in (root, base, base / "current.json", base / "releases")):
        raise ValueError("linked deployment paths forbidden")
    return base


def _app(data, version):
    try:
        app = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("invalid app description") from exc
    if (not isinstance(app, dict) or
        set(app) != {"service", "version", "health", "quality", "demo_only", "rows"} or
        app["service"] != "datapulse-training" or app["version"] != version or
        app["health"] not in ("ready", "failed") or
        app["quality"] not in ("passed", "blocked") or app["demo_only"] is not True or
        type(app["rows"]) is not int or not 0 <= app["rows"] <= 100_000):
        raise ValueError("invalid app contract")
    return app


def build_release(source, output, version):
    """Produce reproducible ZIP and a content-hash manifest, with fixed file allowlist."""
    _version(version)
    source, output = Path(source), Path(output)
    if not source.is_dir() or source.is_symlink():
        raise ValueError("invalid source directory")
    content = {}
    for name in ("README.txt", "app.json"):
        p = source / name
        if not p.is_file() or p.is_symlink():
            raise ValueError("missing or linked build input")
        content[name] = p.read_bytes()
        if len(content[name]) > 16_384:
            raise ValueError("build input too large")
    if not content["README.txt"].strip():
        raise ValueError("empty README")
    _app(content["app.json"], version)
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ("README.txt", "app.json"):
            info = ZipInfo(name, STAMP)
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, content[name])
    raw = buffer.getvalue()
    artifact = "datapulse-" + version + ".zip"
    metadata = {
        "format": "zip-v1", "version": version, "artifact": artifact,
        "sha256": sha256(raw).hexdigest(), "size": len(raw),
    }
    bundle = output / artifact
    manifest = output / ("datapulse-" + version + ".manifest.json")
    if (bundle.exists() and sha256(bundle.read_bytes()).hexdigest() !=
        metadata["sha256"]):
        raise ValueError("cannot overwrite an immutable version")
    _atomic(bundle, raw)
    _atomic(manifest, _json(metadata))
    return bundle, manifest


def verify_release(bundle, manifest):
    """Detect tampered bytes, unsafe members and unexpected release metadata."""
    bundle, manifest = Path(bundle), Path(manifest)
    if bundle.is_symlink() or manifest.is_symlink():
        raise ValueError("linked release forbidden")
    try:
        m = json.loads(manifest.read_text())
    except (ValueError, OSError) as exc:
        raise ValueError("invalid manifest") from exc
    if not isinstance(m, dict) or set(m) != {"format", "version", "artifact", "sha256", "size"}:
        raise ValueError("invalid manifest fields")
    _version(m["version"])
    if (m["format"] != "zip-v1" or m["artifact"] != "datapulse-" + m["version"] + ".zip" or
        not isinstance(m["sha256"], str) or not DIGEST.fullmatch(m["sha256"]) or
        type(m["size"]) is not int or not 100 <= m["size"] <= 100_000 or
        bundle.name != m["artifact"]):
        raise ValueError("unsupported manifest")
    raw = bundle.read_bytes()
    if len(raw) != m["size"] or sha256(raw).hexdigest() != m["sha256"]:
        raise ValueError("checksum mismatch")
    try:
        with ZipFile(BytesIO(raw)) as archive:
            if archive.namelist() != ["README.txt", "app.json"]:
                raise ValueError("unexpected archive entries")
            for info in archive.infolist():
                mode = (info.external_attr >> 16) & 0o170000
                if info.is_dir() or info.file_size > 16_384 or mode == 0o120000:
                    raise ValueError("unsafe archive entry")
            if not archive.read("README.txt").strip():
                raise ValueError("empty README")
            app = _app(archive.read("app.json"), m["version"])
    except (OSError, KeyError) as exc:
        raise ValueError("unreadable archive") from exc
    return {"metadata": m, "app": app}


def _pointer(base):
    path = base / "current.json"
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        raise ValueError("corrupt deployment pointer") from exc
    if not isinstance(value, dict) or set(value) != {"version", "sha256", "previous"}:
        raise ValueError("invalid deployment pointer")
    for entry in (value, value["previous"]):
        if entry is None:
            continue
        if not isinstance(entry, dict) or "version" not in entry or "sha256" not in entry:
            raise ValueError("invalid deployment reference")
        _version(entry["version"])
        if not isinstance(entry["sha256"], str) or not DIGEST.fullmatch(entry["sha256"]):
            raise ValueError("invalid deployment digest")
    return value


def _installed(base, entry):
    digest = entry["sha256"]
    archive = base / "releases" / (digest + ".zip")
    metadata = base / "releases" / (digest + ".json")
    if archive.is_symlink() or metadata.is_symlink():
        raise ValueError("unsafe stored release")
    # A verified bundle must retain the original artifact filename for validation.
    inspected = verify_release_named(archive, metadata)
    if (inspected["metadata"]["sha256"] != digest or
        inspected["metadata"]["version"] != entry["version"]):
        raise ValueError("stored release metadata mismatch")
    if inspected["app"]["health"] != "ready" or inspected["app"]["quality"] != "passed":
        raise ValueError("stored release fails health")
    return inspected


def verify_release_named(archive, metadata):
    """Verify content-addressed copies without relying on original basename."""
    data = json.loads(Path(metadata).read_text())
    return verify_release_proxy(archive, metadata, data)


def verify_release_proxy(archive, metadata, data):
    """Recheck saved archive using temporary original filename validation in memory."""
    if not isinstance(data, dict) or not isinstance(data.get("version"), str):
        raise ValueError("bad saved manifest")
    _version(data["version"])
    expected_name = "datapulse-" + data["version"] + ".zip"
    if data.get("artifact") != expected_name:
        raise ValueError("unexpected saved artifact name")
    # Same bytes, same checks as verify_release; the filename is an internal digest key.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix="stage09-verify-") as directory:
        copy = Path(directory) / expected_name
        _atomic(copy, Path(archive).read_bytes())
        return verify_release(copy, metadata)


def deploy_release(bundle, manifest, root, environment,
                   *, fail_health=False, crash_before_switch=False):
    """Stage validated bytes; atomically switch a simulated environment pointer."""
    checked = verify_release(bundle, manifest)
    base = _env(root, environment)
    prior = _pointer(base)
    digest = checked["metadata"]["sha256"]
    entry = {"version": checked["metadata"]["version"], "sha256": digest}
    if prior is not None:
        _installed(base, prior)
        if prior["sha256"] == digest:
            return {"status": "already_current", "environment": environment, **entry}
    if (fail_health or checked["app"]["health"] != "ready" or
        checked["app"]["quality"] != "passed"):
        raise ValueError("health or quality gate failed")
    releases = base / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    for source, filename in ((bundle, digest + ".zip"), (manifest, digest + ".json")):
        destination = releases / filename
        if destination.is_symlink():
            raise ValueError("linked stored artifact")
        raw = Path(source).read_bytes()
        if destination.exists() and destination.read_bytes() != raw:
            raise ValueError("immutable stored artifact changed")
        if not destination.exists():
            _atomic(destination, raw)
    _installed(base, entry)
    if crash_before_switch:
        raise RuntimeError("simulated failure before atomic switch")
    _atomic(base / "current.json", _json({
        **entry,
        "previous": None if prior is None else
                    {"version": prior["version"], "sha256": prior["sha256"]},
    }))
    return {"status": "deployed", "environment": environment, **entry}


def rollback_release(root, environment):
    """Revert pointer to previously validated bundle, preserving forward version."""
    base = _env(root, environment)
    active = _pointer(base)
    if active is None or active["previous"] is None:
        raise ValueError("no previous release")
    _installed(base, active)
    previous = active["previous"]
    _installed(base, previous)
    _atomic(base / "current.json", _json({
        **previous,
        "previous": {"version": active["version"], "sha256": active["sha256"]},
    }))
    return {"status": "rolled_back", "environment": environment, **previous}


def deployment_status(root, environment):
    base = _env(root, environment)
    current = _pointer(base)
    if current is None:
        return {"status": "empty", "environment": environment}
    _installed(base, current)
    return {"status": "ready", "environment": environment,
            "version": current["version"], "sha256": current["sha256"],
            "rollback_available": current["previous"] is not None}

