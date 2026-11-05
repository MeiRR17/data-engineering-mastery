"""Pure unit tests for the PostgreSQL Docker final-startup readiness gate."""
from types import SimpleNamespace
import unittest

from scripts.docker_pg_ready import INITIALIZATION_FINISHED, wait_for_final_postgres


class DockerPostgresReadinessTests(unittest.TestCase):
    def test_initial_temp_server_is_not_mistaken_for_final(self):
        commands = []
        def runner(argv, **_kwargs):
            commands.append(argv)
            if argv[1] == "logs":
                return SimpleNamespace(returncode=0, stdout="server is ready to accept connections", stderr="")
            return SimpleNamespace(returncode=0)
        with self.assertRaises(RuntimeError):
            wait_for_final_postgres("pg-temp", attempts=3, runner=runner,
                                    sleeper=lambda seconds: None)
        self.assertEqual(len(commands), 3)
        self.assertTrue(all(call[1] == "logs" for call in commands))

    def test_final_entrypoint_marker_and_pg_isready_are_both_required(self):
        calls = []
        def runner(argv, **_kwargs):
            calls.append(argv)
            if argv[1] == "logs":
                return SimpleNamespace(returncode=0,
                                       stdout=INITIALIZATION_FINISHED, stderr="")
            return SimpleNamespace(returncode=0)
        wait_for_final_postgres("pg-ready", attempts=2, runner=runner,
                                sleeper=lambda seconds: None)
        self.assertEqual([call[1] for call in calls], ["logs", "exec"])

    def test_final_startup_can_take_more_than_one_probe(self):
        counter = {"exec": 0}
        sleeps = []
        def runner(argv, **_kwargs):
            if argv[1] == "logs":
                return SimpleNamespace(returncode=0, stdout="",
                                       stderr=INITIALIZATION_FINISHED)
            counter["exec"] += 1
            return SimpleNamespace(returncode=1 if counter["exec"] == 1 else 0)
        wait_for_final_postgres("pg-late", attempts=3, runner=runner,
                                sleeper=sleeps.append)
        self.assertEqual(counter["exec"], 2)
        self.assertEqual(sleeps, [1])

    def test_no_final_marker_fails_closed(self):
        def runner(argv, **_kwargs):
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        with self.assertRaises(RuntimeError):
            wait_for_final_postgres("pg-never", attempts=2, runner=runner,
                                    sleeper=lambda seconds: None)

    def test_bad_arguments_rejected(self):
        with self.assertRaises(ValueError):
            wait_for_final_postgres("")
        with self.assertRaises(ValueError):
            wait_for_final_postgres("pg", attempts=0)

