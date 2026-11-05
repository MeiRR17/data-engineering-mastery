"""Stage 09 grader: --reference validates instructor code; default grades starter.

Creates disposable directories only. No external accounts, Docker or internet.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

LAB = Path(__file__).resolve().parent
TARGET = None


class DeliveryScenarios(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="stage09-grade-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.deployments = self.root / "simulated-environments"
        self.number = 0

    def source(self, version="v1.0.0", *, health="ready", quality="passed", rows=4):
        self.number += 1
        source = self.root / ("src-" + str(self.number))
        source.mkdir()
        (source / "README.txt").write_text(
            "Synthetic training release, no external connections.\n", encoding="utf8"
        )
        app = {"service": "datapulse-training", "version": version,
               "health": health, "quality": quality, "demo_only": True, "rows": rows}
        (source / "app.json").write_text(json.dumps(app), encoding="utf8")
        return source

    def build(self, version="v1.0.0", **kwargs):
        source = self.source(version, **kwargs)
        return TARGET.build_release(source, self.root / ("artifacts-" + str(self.number)), version)

    def deploy(self, version="v1.0.0", environment="dev", **kwargs):
        bundle, manifest = self.build(version)
        return TARGET.deploy_release(bundle, manifest, self.deployments, environment, **kwargs)

    def test_build_is_reproducible(self):
        first, _ = self.build()
        second, _ = self.build()
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_manifest_matches_artifact_sha(self):
        bundle, manifest = self.build()
        record = TARGET.verify_release(bundle, manifest)["metadata"]
        self.assertEqual(record["sha256"], sha256(bundle.read_bytes()).hexdigest())
        self.assertEqual(record["size"], len(bundle.read_bytes()))

    def test_version_string_rejected_if_unsafe(self):
        for version in ("latest", "v1.0", "v1.0.0/../../", "v1.0.0-beta", ""):
            with self.subTest(version=version), self.assertRaises(ValueError):
                TARGET.build_release(self.source(), self.root / "artifacts", version)

    def test_app_version_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            TARGET.build_release(self.source("v1.0.0"),
                                 self.root / "artifacts", "v2.0.0")

    def test_source_symlink_rejected(self):
        source = self.source()
        (source / "README.txt").unlink()
        (source / "README.txt").symlink_to(self.root / "missing.txt")
        with self.assertRaises(ValueError):
            TARGET.build_release(source, self.root / "out", "v1.0.0")

    def test_source_oversized_rejected(self):
        source = self.source()
        (source / "README.txt").write_text("x" * 20_000)
        with self.assertRaises(ValueError):
            TARGET.build_release(source, self.root / "out", "v1.0.0")

    def test_modified_bundle_fails_checksum(self):
        bundle, manifest = self.build()
        bundle.write_bytes(bundle.read_bytes() + b"attack")
        with self.assertRaises(ValueError):
            TARGET.verify_release(bundle, manifest)

    def test_modified_manifest_fails_integrity(self):
        bundle, manifest = self.build()
        data = json.loads(manifest.read_text())
        data["sha256"] = "0" * 64
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            TARGET.verify_release(bundle, manifest)

    def test_extra_zip_member_rejected_even_with_new_checksum(self):
        bundle, manifest = self.build()
        with ZipFile(bundle, mode="a", compression=ZIP_DEFLATED) as zf:
            zf.writestr("../pwned.txt", "unexpected")
        data = json.loads(manifest.read_text())
        data["sha256"] = sha256(bundle.read_bytes()).hexdigest()
        data["size"] = len(bundle.read_bytes())
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            TARGET.verify_release(bundle, manifest)

    def test_extra_source_file_not_packaged(self):
        source = self.source()
        (source / "private.txt").write_text("do not publish")
        bundle, _ = TARGET.build_release(source, self.root / "out", "v1.0.0")
        with ZipFile(bundle) as zf:
            self.assertEqual(zf.namelist(), ["README.txt", "app.json"])
            self.assertNotIn(b"do not publish", bundle.read_bytes())

    def test_empty_environment_status(self):
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev"),
                         {"status": "empty", "environment": "dev"})

    def test_first_deploy_is_readable(self):
        result = self.deploy()
        self.assertEqual(result["status"], "deployed")
        status = TARGET.deployment_status(self.deployments, "dev")
        self.assertEqual(status["version"], "v1.0.0")
        self.assertEqual(status["status"], "ready")
        self.assertFalse(status["rollback_available"])

    def test_repeat_deploy_does_not_replace_pointer(self):
        bundle, manifest = self.build()
        TARGET.deploy_release(bundle, manifest, self.deployments, "dev")
        pointer = self.deployments / "dev/current.json"
        original = pointer.read_bytes()
        result = TARGET.deploy_release(bundle, manifest, self.deployments, "dev")
        self.assertEqual(result["status"], "already_current")
        self.assertEqual(pointer.read_bytes(), original)

    def test_health_failure_blocks_promotion(self):
        self.deploy()
        before = TARGET.deployment_status(self.deployments, "dev")["sha256"]
        with self.assertRaises(ValueError):
            self.deploy("v2.0.0", health="failed")
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["sha256"], before)

    def test_quality_gate_blocks_promotion(self):
        self.deploy()
        with self.assertRaises(ValueError):
            self.deploy("v2.0.0", quality="blocked")
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["version"],
                         "v1.0.0")

    def test_forced_health_failure_blocks_promotion(self):
        bundle, manifest = self.build()
        with self.assertRaises(ValueError):
            TARGET.deploy_release(bundle, manifest, self.deployments, "dev",
                                  fail_health=True)
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["status"], "empty")

    def test_crash_before_switch_keeps_previous_release(self):
        self.deploy()
        with self.assertRaises(RuntimeError):
            self.deploy("v2.0.0", crash_before_switch=True)
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["version"],
                         "v1.0.0")

    def test_second_promotion_then_rollback(self):
        self.deploy()
        self.deploy("v2.0.0")
        self.assertTrue(TARGET.deployment_status(self.deployments, "dev")["rollback_available"])
        result = TARGET.rollback_release(self.deployments, "dev")
        self.assertEqual(result["status"], "rolled_back")
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["version"],
                         "v1.0.0")

    def test_rollback_rejected_if_no_previous_release(self):
        self.deploy()
        with self.assertRaises(ValueError):
            TARGET.rollback_release(self.deployments, "dev")

    def test_corrupt_old_release_blocks_rollback(self):
        first = self.deploy()
        self.deploy("v2.0.0")
        archive = self.deployments / "dev/releases" / (first["sha256"] + ".zip")
        archive.write_bytes(archive.read_bytes() + b"tamper")
        with self.assertRaises(ValueError):
            TARGET.rollback_release(self.deployments, "dev")
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["version"],
                         "v2.0.0")

    def test_environment_isolation(self):
        self.deploy("v1.0.0", "dev")
        self.deploy("v2.0.0", "staging")
        self.assertEqual(TARGET.deployment_status(self.deployments, "dev")["version"],
                         "v1.0.0")
        self.assertEqual(TARGET.deployment_status(self.deployments, "staging")["version"],
                         "v2.0.0")
        self.assertEqual(TARGET.deployment_status(self.deployments, "prod-sim")["status"],
                         "empty")

    def test_only_simulated_environment_names_allowed(self):
        bundle, manifest = self.build()
        for bad in ("production", "../etc", "", "DEV", "prod"):
            with self.subTest(environment=bad), self.assertRaises(ValueError):
                TARGET.deploy_release(bundle, manifest, self.deployments, bad)

    def test_corrupt_active_pointer_rejected(self):
        self.deploy()
        pointer = self.deployments / "dev/current.json"
        pointer.write_text('{"version":"v9.9.9","sha256":"../evil"}')
        with self.assertRaises(ValueError):
            TARGET.deployment_status(self.deployments, "dev")

    def test_same_version_cannot_overwrite_other_content(self):
        bundle, _ = self.build()
        another = self.source()
        (another / "README.txt").write_text("Different build payload.")
        with self.assertRaises(ValueError):
            TARGET.build_release(another, bundle.parent, "v1.0.0")

    def test_empty_readme_rejected(self):
        source = self.source()
        (source / "README.txt").write_text("")
        with self.assertRaises(ValueError):
            TARGET.build_release(source, self.root / "out", "v1.0.0")

    def test_root_symlink_is_rejected(self):
        actual = self.root / "real"
        actual.mkdir()
        linked = self.root / "link"
        linked.symlink_to(actual, target_is_directory=True)
        bundle, manifest = self.build()
        with self.assertRaises(ValueError):
            TARGET.deploy_release(bundle, manifest, linked, "dev")


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    path = LAB / ("instructor/reference.py" if args.reference else "starter.py")
    spec = spec_from_file_location("stage09_target", path)
    TARGET = module_from_spec(spec)
    spec.loader.exec_module(TARGET)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryScenarios)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

