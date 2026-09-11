import importlib.util
import math
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

    def test_boolean_budget_values_are_rejected(self):
        policy = {
            "provider": "openai",
            "daily_cap_usd": True,
            "monthly_cap_usd": False,
            "alert_threshold_pct": True,
            "owner": "platform",
        }

        warnings = provider_budget.provider_budget_warnings(policy)

        self.assertIn("daily_cap_usd_must_be_positive", warnings)
        self.assertIn("monthly_cap_usd_must_be_positive", warnings)
        self.assertIn("alert_threshold_pct_must_be_1_to_100", warnings)

    def test_non_finite_budget_values_are_rejected(self):
        base_policy = {
            "provider": "openai",
            "daily_cap_usd": 25,
            "monthly_cap_usd": 500,
            "alert_threshold_pct": 80,
            "owner": "platform",
        }
        expected_warning = {
            "daily_cap_usd": "daily_cap_usd_must_be_positive",
            "monthly_cap_usd": "monthly_cap_usd_must_be_positive",
            "alert_threshold_pct": "alert_threshold_pct_must_be_1_to_100",
        }

        for field, warning in expected_warning.items():
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(field=field, value=value):
                    policy = dict(base_policy)
                    policy[field] = value
                    self.assertIn(
                        warning,
                        provider_budget.provider_budget_warnings(policy),
                    )


if __name__ == "__main__":
    unittest.main()
