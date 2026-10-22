import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.litellm_route_contract import validate_workload_contracts


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "litellm-routes.example.json"


class LiteLlmRouteContractTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_example_contract_is_valid_without_provider_calls(self):
        self.assertEqual([], validate_workload_contracts(self.config))

    def test_fallback_must_preserve_required_capabilities(self):
        config = copy.deepcopy(self.config)
        config["routes"][1]["capabilities"]["json_mode"] = False

        errors = validate_workload_contracts(config)

        self.assertIn("rag-claude: capability json_mode is required", errors)

    def test_workload_route_and_shape_are_required(self):
        config = copy.deepcopy(self.config)
        config["workloads"] = [
            {
                "id": "rag-chat",
                "route": "missing",
                "required_capabilities": [],
                "required_context_tokens": 0,
            }
        ]

        errors = validate_workload_contracts(config)

        self.assertIn("workloads[0]: route missing is not defined", errors)
        self.assertIn(
            "workloads[0].required_capabilities must be a non-empty unique list", errors
        )
        self.assertIn(
            "workloads[0].required_context_tokens must be a positive integer", errors
        )

    def test_json_cli_exposes_route_and_fallback_evidence(self):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/litellm_route_contract.py",
                "--config",
                str(CONFIG_PATH),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(
            ["rag-default", "rag-claude"],
            report["workloads"][0]["fallback_chain"],
        )
        self.assertEqual([], report["errors"])
        self.assertEqual("", result.stderr)

    def test_malformed_route_shape_returns_json_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.json"
            config_path.write_text(
                json.dumps({"routes": "invalid", "workloads": {}}),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/litellm_route_contract.py",
                    "--config",
                    str(config_path),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        report = json.loads(result.stdout)
        self.assertEqual(1, result.returncode)
        self.assertFalse(report["ok"])
        self.assertIn("routes must be a non-empty list", report["errors"])
        self.assertIn("workloads must be a non-empty list", report["errors"])


if __name__ == "__main__":
    unittest.main()
