import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CheckStackTests(unittest.TestCase):
    def test_plan_lists_observable_endpoints(self):
        result = subprocess.run(
            ["bash", "scripts/check-stack.sh", "--plan"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

        self.assertIn("vector-db", result.stdout)
        self.assertIn("prometheus", result.stdout)
        self.assertIn("grafana", result.stdout)
        self.assertIn("litellm-config", result.stdout)

    def test_strict_mode_delegates_readiness_to_the_collector(self):
        with tempfile.TemporaryDirectory() as directory:
            command_directory = Path(directory)
            self._write_command(
                command_directory,
                "python3",
                'if [ "$1" = "scripts/litellm_preflight.py" ]; then exit 0; fi; case "$*" in *"--require-ready"*) exit 0 ;; *) exit 7 ;; esac',
            )
            self._write_command(command_directory, "docker", "exit 0")

            result = self._run_stack_check(command_directory, strict="true")

        self.assertEqual(0, result.returncode)
        self.assertIn("Platform readiness", result.stdout)

    def test_invalid_strict_mode_is_rejected_before_running_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._run_stack_check(Path(directory), strict="sometimes")

        self.assertEqual(2, result.returncode)
        self.assertIn("STRICT must be either true or false", result.stderr)

    def _run_stack_check(self, command_directory: Path, *, strict: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ | {
            "PATH": str(command_directory),
            "STRICT": strict,
        }
        return subprocess.run(
            ["/bin/bash", "scripts/check-stack.sh"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

    @staticmethod
    def _write_command(directory: Path, name: str, body: str) -> None:
        path = directory / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
