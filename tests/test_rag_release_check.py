from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock

from scripts.rag_release_check import (
    ManifestError,
    load_manifest,
    main,
    run_release_checks,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_MANIFEST = ROOT / "examples" / "release-checks.example.json"


class ReleaseCheckManifestTests(unittest.TestCase):
    def test_example_manifest_is_valid_and_normalized(self):
        manifest = load_manifest(EXAMPLE_MANIFEST)

        self.assertEqual(1, manifest["schema_version"])
        self.assertEqual(5, len(manifest["checks"]))

    def test_unknown_gate_and_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(ManifestError, "must be one of"):
            validate_manifest(
                {
                    "schema_version": 1,
                    "checks": [{"id": "unsafe", "gate": "arbitrary-command"}],
                }
            )

        with self.assertRaisesRegex(ManifestError, "duplicate check id"):
            validate_manifest(
                {
                    "schema_version": 1,
                    "checks": [
                        {"id": "routes", "gate": "litellm-preflight"},
                        {"id": "routes", "gate": "vector-backup"},
                    ],
                }
            )

    def test_unsupported_version_and_unknown_fields_are_rejected(self):
        with self.assertRaisesRegex(ManifestError, "schema_version must be 1"):
            validate_manifest({"schema_version": 2, "checks": []})

        with self.assertRaisesRegex(ManifestError, "unsupported fields"):
            validate_manifest(
                {
                    "schema_version": 1,
                    "checks": [{"id": "routes", "gate": "litellm-preflight"}],
                    "command": "python arbitrary.py",
                }
            )


class ReleaseCheckRunnerTests(unittest.TestCase):
    def test_example_runs_all_offline_gates(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main([str(EXAMPLE_MANIFEST)])

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(
            {"errors": 0, "failed": 0, "passed": 5, "total": 5},
            report["summary"],
        )

    def test_policy_rejection_returns_one(self):
        manifest = {
            "schema_version": 1,
            "checks": [{"id": "backup", "gate": "vector-backup", "args": ["--json"]}],
        }
        with tempfile.TemporaryDirectory() as temp_directory:
            manifest_path = Path(temp_directory) / "release-checks.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main([str(manifest_path)])

        report = json.loads(output.getvalue())
        self.assertEqual(1, exit_code)
        self.assertEqual("fail", report["status"])
        self.assertEqual(1, report["summary"]["failed"])

    def test_timeout_is_an_execution_error(self):
        runner = Mock(side_effect=subprocess.TimeoutExpired(["python"], 3))
        manifest = validate_manifest(
            {
                "schema_version": 1,
                "checks": [{"id": "routes", "gate": "litellm-preflight"}],
            }
        )

        report = run_release_checks(
            manifest,
            manifest_directory=ROOT,
            timeout_seconds=3,
            runner=runner,
        )

        self.assertEqual("error", report["status"])
        self.assertEqual(1, report["summary"]["errors"])
        command = runner.call_args.args[0]
        self.assertEqual("litellm_preflight.py", Path(command[1]).name)
        self.assertNotIn("shell", runner.call_args.kwargs)

    def test_invalid_manifest_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            manifest_path = Path(temp_directory) / "release-checks.json"
            manifest_path.write_text('{"schema_version": 99}', encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                exit_code = main([str(manifest_path)])

        report = json.loads(error.getvalue())
        self.assertEqual(2, exit_code)
        self.assertEqual("error", report["status"])
        self.assertIn("schema_version", report["error"])


if __name__ == "__main__":
    unittest.main()
