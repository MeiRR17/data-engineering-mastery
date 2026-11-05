"""Test readiness reporting without installing extensions or touching the user machine."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "verify_learning_environment.py"
spec = spec_from_file_location("readiness", path)
readiness = module_from_spec(spec)
spec.loader.exec_module(readiness)


class ReadinessTests(TestCase):
    def test_extension_parser_accepts_real_vscode_format(self):
        text = "ms-python.python@2026.17.2\nMS-TOOLSAI.JUPYTER@2026.8.0\nunrelated warning\n"
        result = readiness.parse_extensions(text)
        self.assertEqual(result["ms-python.python"], "2026.17.2")
        self.assertEqual(result["ms-toolsai.jupyter"], "2026.8.0")
        self.assertNotIn("unrelated warning", result)

    def test_missing_cli_is_a_failure_not_a_false_success(self):
        with mock.patch.object(readiness, "find_code_cli", return_value=None):
            installed, errors = readiness.check_extensions()
        self.assertEqual(installed, {})
        self.assertEqual(errors, ["VSCODE_CLI_MISSING"])

    def test_incomplete_extension_installation_is_detected(self):
        output = "ms-python.python@2026.1.0\n"
        fake = mock.Mock(returncode=0, stdout=output)
        with mock.patch.object(readiness, "find_code_cli", return_value="code"):
            with mock.patch.object(readiness.subprocess, "run", return_value=fake):
                installed, errors = readiness.check_extensions()
        self.assertEqual(installed["ms-python.python"], "2026.1.0")
        self.assertEqual(len(errors), 3)

    def test_failure_is_not_reported_as_pass(self):
        with mock.patch.object(readiness, "check_extensions", return_value=({}, ["EXTENSION_MISSING:fake"])):
            with mock.patch.object(readiness, "check_packages", return_value=({}, ["PACKAGE_MISSING:nbclient"])):
                result = readiness.verify("smoke")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RUNTIME_NOT_READY", result["issues"])
        self.assertEqual(result["execution_scope"], "THIS_CLI_CONTEXT_ONLY")

    def test_report_contains_no_local_username_or_machine_paths(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "setup-check.local.json"
            report = {"status": "PASS", "installed_extensions": {"ms-python.python": "1.2.3"}}
            with mock.patch.object(readiness, "REPORT", target):
                readiness.write_local_report(report)
            self.assertEqual(target.read_text(encoding="utf-8").count("PASS"), 1)

    def test_report_symlink_is_not_overwritten(self):
        with TemporaryDirectory() as folder:
            original = Path(folder) / "original.txt"
            original.write_text("untouched")
            alias = Path(folder) / "setup-check.local.json"
            alias.symlink_to(original)
            with mock.patch.object(readiness, "REPORT", alias):
                with self.assertRaises(RuntimeError):
                    readiness.write_local_report({"status": "PASS"})
            self.assertEqual(original.read_text(), "untouched")


if __name__ == "__main__":
    import unittest
    unittest.main()
