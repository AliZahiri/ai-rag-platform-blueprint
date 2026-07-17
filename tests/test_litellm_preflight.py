import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.litellm_preflight import load_config, validate_config, validation_report


VALID_CONFIG = {
    "routes": [
        {
            "alias": "rag-default",
            "provider": "openai",
            "model": "gpt-4.1-mini",
            "env_key": "OPENAI_API_KEY",
            "fallbacks": ["rag-fallback"],
            "limits": {
                "rpm": 120,
                "tpm": 200000,
                "max_retries": 2,
                "timeout_seconds": 60,
                "cost_cap_usd": 25.0,
            },
            "capabilities": {
                "streaming": True,
                "tool_calling": True,
                "json_mode": True,
                "context_window": 128000,
            },
        },
        {
            "alias": "rag-fallback",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-latest",
            "env_key": "ANTHROPIC_API_KEY",
            "fallbacks": [],
            "limits": {
                "rpm": 60,
                "tpm": 150000,
                "max_retries": 2,
                "timeout_seconds": 60,
                "cost_cap_usd": 25.0,
            },
            "capabilities": {
                "streaming": True,
                "tool_calling": True,
                "json_mode": True,
                "context_window": 200000,
            },
        },
    ],
    "observability": {
        "latency": True,
        "tokens": True,
        "cost": True,
        "failures": True,
    },
}


class LiteLlmPreflightTests(unittest.TestCase):
    def test_example_config_is_valid_without_provider_calls(self):
        config = load_config(Path("configs/litellm-routes.example.json"))

        self.assertEqual(validate_config(config), [])

    def test_missing_secret_is_reported_only_when_required(self):
        config = copy.deepcopy(VALID_CONFIG)
        original = os.environ.pop("OPENAI_API_KEY", None)
        try:
            errors = validate_config(config, require_secrets=True)
        finally:
            if original is not None:
                os.environ["OPENAI_API_KEY"] = original

        self.assertIn("rag-default: required environment secret OPENAI_API_KEY is missing", errors)

    def test_dangling_fallback_is_reported(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][0]["fallbacks"] = ["missing-route"]

        errors = validate_config(config)

        self.assertIn("rag-default: fallback missing-route is not defined as a route alias", errors)

    def test_missing_model_route_is_reported(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][0]["model"] = ""

        errors = validate_config(config)

        self.assertIn("rag-default: model is required", errors)

    def test_fallback_cycle_is_reported(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][1]["fallbacks"] = ["rag-default"]

        errors = validate_config(config)

        self.assertTrue(any("fallback cycle detected" in error for error in errors))

    def test_required_capabilities_are_enforced(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][0]["capabilities"]["json_mode"] = False
        config["routes"][0]["capabilities"]["context_window"] = 2048

        errors = validate_config(config, min_context_window=8192)

        self.assertIn("rag-default: capabilities.json_mode must be true for the RAG route", errors)
        self.assertIn("rag-default: capabilities.context_window must be at least 8192", errors)

    def test_route_aliases_must_be_stable_slug_values(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][0]["alias"] = "RAG Default"

        errors = validate_config(config)

        self.assertIn(
            "RAG Default: alias must use lowercase letters, numbers, and hyphens",
            errors,
        )

    def test_validation_report_has_stable_machine_readable_fields(self):
        report = validation_report(["invalid"], live_probe_requested=True)

        self.assertEqual(
            report,
            {
                "ok": False,
                "errors": ["invalid"],
                "live_probe_requested": True,
            },
        )

    def test_json_cli_reports_valid_config(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/litellm_preflight.py",
                "--config",
                "configs/litellm-routes.example.json",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "ok": True,
                "errors": [],
                "live_probe_requested": False,
            },
        )
        self.assertEqual(result.stderr, "")

    def test_json_cli_reports_invalid_config_and_nonzero_exit(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["routes"][0]["model"] = ""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/litellm_preflight.py",
                    "--config",
                    str(config_path),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertIn("rag-default: model is required", report["errors"])
        self.assertFalse(report["live_probe_requested"])
        self.assertEqual(result.stderr, "")

    def test_json_cli_keeps_live_probe_notice_inside_report(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/litellm_preflight.py",
                "--config",
                "configs/litellm-routes.example.json",
                "--live-probe",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertTrue(json.loads(result.stdout)["live_probe_requested"])
        self.assertEqual(result.stdout.count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
