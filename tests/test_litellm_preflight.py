import copy
import os
import unittest
from pathlib import Path

from scripts.litellm_preflight import load_config, validate_config


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


if __name__ == "__main__":
    unittest.main()
