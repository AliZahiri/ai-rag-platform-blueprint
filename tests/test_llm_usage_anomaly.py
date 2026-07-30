import unittest

from scripts.llm_usage_anomaly import usage_anomaly_violations, usage_is_within_expected_bounds


class LlmUsageAnomalyGateTests(unittest.TestCase):
    def test_observation_within_absolute_and_baseline_budgets_passes(self):
        observation = {"prompt_tokens": 600, "completion_tokens": 200, "cost_usd": 0.03}
        self.assertTrue(usage_is_within_expected_bounds(observation, maximum_prompt_tokens=1000, maximum_completion_tokens=500, maximum_cost_usd=0.05, baseline_total_tokens=500, maximum_growth_ratio=2))

    def test_absolute_and_relative_anomalies_are_reported_together(self):
        observation = {"prompt_tokens": 1200, "completion_tokens": 600, "cost_usd": 0.08}
        violations = usage_anomaly_violations(observation, maximum_prompt_tokens=1000, maximum_completion_tokens=500, maximum_cost_usd=0.05, baseline_total_tokens=500, maximum_growth_ratio=2)
        self.assertIn("prompt_tokens_exceed_budget", violations)
        self.assertIn("completion_tokens_exceed_budget", violations)
        self.assertIn("cost_usd_exceeds_budget", violations)
        self.assertIn("total_token_growth_exceeds_ratio", violations)

    def test_invalid_observation_and_policy_values_fail(self):
        violations = usage_anomaly_violations({"prompt_tokens": True, "completion_tokens": -1, "cost_usd": float("nan")}, maximum_prompt_tokens=1000, maximum_completion_tokens=500, maximum_cost_usd=0.05)
        self.assertEqual(3, len(violations))
        with self.assertRaises(ValueError):
            usage_anomaly_violations({}, maximum_prompt_tokens=-1, maximum_completion_tokens=1, maximum_cost_usd=1)


if __name__ == "__main__":
    unittest.main()
