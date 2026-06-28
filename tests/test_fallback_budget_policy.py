import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/fallback_budget_policy.py"
SPEC = importlib.util.spec_from_file_location("fallback_budget_policy", SCRIPT_PATH)
fallback_budget_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fallback_budget_policy)


class FallbackBudgetPolicyTests(unittest.TestCase):
    def test_safe_fallback_budget_passes(self):
        policy = {"fallback_alias": "rag-fallback", "estimated_cost_usd": 0.05, "request_budget_usd": 0.10, "retry_count": 1, "required_capabilities_preserved": True}

        self.assertTrue(fallback_budget_policy.fallback_budget_is_safe(policy))

    def test_expensive_fallback_is_reported(self):
        warnings = fallback_budget_policy.fallback_budget_warnings({"fallback_alias": "rag-fallback", "estimated_cost_usd": 1.5, "request_budget_usd": 1.0})

        self.assertIn("fallback_cost_exceeds_request_budget", warnings)
        self.assertIn("required_capabilities_must_be_preserved", warnings)

    def test_retry_count_is_bounded(self):
        warnings = fallback_budget_policy.fallback_budget_warnings(
            {
                "fallback_alias": "rag-fallback",
                "estimated_cost_usd": 0.05,
                "request_budget_usd": 0.10,
                "retry_count": 3,
                "required_capabilities_preserved": True,
            }
        )

        self.assertIn("retry_count_exceeds_fallback_policy", warnings)


if __name__ == "__main__":
    unittest.main()
