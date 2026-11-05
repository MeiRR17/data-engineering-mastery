
"""Exercise a two-environment release, a failed promotion and an atomic rollback.

Creates ONLY temporary training files, no network, credentials or real deploys.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json

from instructor.reference import (
    build_release, deploy_release, deployment_status, rollback_release,
)


def source(path, version, *, health="ready", quality="passed", rows=4):
    path.mkdir(parents=True)
    (path / "README.txt").write_text("Synthetic-only DataPulse training artifact.\n")
    (path / "app.json").write_text(
        json.dumps({"service": "datapulse-training", "version": version,
                    "health": health, "quality": quality,
                    "demo_only": True, "rows": rows}),
        encoding="utf-8",
    )
    return path


def main():
    with TemporaryDirectory(prefix="stage09-local-release-") as folder:
        root = Path(folder)
        deployments = root / "environments"
        v1 = build_release(source(root / "source-v1", "v1.0.0"),
                           root / "artifacts-v1", "v1.0.0")
        v2 = build_release(source(root / "source-v2", "v1.1.0", rows=5),
                           root / "artifacts-v2", "v1.1.0")
        broken = build_release(
            source(root / "source-broken", "v1.2.0", health="failed"),
            root / "artifacts-broken", "v1.2.0"
        )
        history = []
        deploy_release(*v1, deployments, "dev")
        history.append({"operation": "deploy-dev", **deployment_status(deployments, "dev")})
        deploy_release(*v1, deployments, "staging")
        deploy_release(*v2, deployments, "staging")
        history.append({"operation": "promote-staging", **deployment_status(deployments, "staging")})
        try:
            deploy_release(*broken, deployments, "staging")
        except ValueError:
            history.append({"operation": "reject-unhealthy", "status": "blocked"})
        else:
            raise RuntimeError("unsafe release incorrectly promoted")
        if deployment_status(deployments, "staging")["version"] != "v1.1.0":
            raise RuntimeError("failure changed active staging release")
        rollback_release(deployments, "staging")
        history.append({"operation": "rollback-staging", **deployment_status(deployments, "staging")})
        if deployment_status(deployments, "dev")["version"] != "v1.0.0":
            raise RuntimeError("staging affected dev")
        if deployment_status(deployments, "staging")["version"] != "v1.0.0":
            raise RuntimeError("rollback failed")
        print(json.dumps({"result": "PASS", "mode": "offline-training", "history": history},
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
