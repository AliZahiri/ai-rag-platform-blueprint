import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/provider_budget.py"
SPEC = importlib.util.spec_from_file_location("provider_budget", SCRIPT_PATH)
provider_budget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider_budget)


class ProviderBudgetTests(unittest.TestCase):
    def test_valid_budget_policy_is_safe(self):
        policy = {
            "provider": "openai",
            "daily_cap_usd": 25,
            "monthly_cap_usd": 500,
            "alert_threshold_pct": 80,
            "owner": "platform",
        }

        self.assertTrue(provider_budget.provider_budget_is_safe(policy))

    def test_invalid_budget_policy_reports_warnings(self):
        warnings = provider_budget.provider_budget_warnings({"daily_cap_usd": 10, "monthly_cap_usd": 5})

        self.assertIn("provider_missing", warnings)
        self.assertIn("monthly_cap_usd_must_cover_daily_cap", warnings)
        self.assertIn("alert_threshold_pct_must_be_1_to_100", warnings)


if __name__ == "__main__":
    unittest.main()
