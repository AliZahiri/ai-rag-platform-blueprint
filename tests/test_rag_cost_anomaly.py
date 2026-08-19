import unittest
from datetime import datetime, timezone

from scripts.rag_cost_anomaly import cost_anomaly_violations, cost_observation_is_within_policy


NOW = datetime(2026, 8, 19, 6, 0, tzinfo=timezone.utc)
POLICY = {"daily_cap_usd": 25.0, "maximum_growth_ratio": 2.0}


class RagCostAnomalyEvidenceGateTests(unittest.TestCase):
    def test_fresh_cost_within_absolute_and_growth_budgets_passes(self):
        observation = {"provider": "primary", "cost_usd": 12.0, "baseline_cost_usd": 8.0, "observed_at": "2026-08-19T05:55:00Z"}
        self.assertTrue(cost_observation_is_within_policy(observation, POLICY, now=NOW))

    def test_missing_invalid_and_anomalous_cost_evidence_fails(self):
        observation = {"provider": "", "cost_usd": 30.0, "baseline_cost_usd": 10.0, "observed_at": "2026-08-19T07:00:00Z"}
        violations = cost_anomaly_violations(observation, POLICY, now=NOW)
        self.assertIn("provider_is_required", violations)
        self.assertIn("cost_usd_exceeds_daily_cap", violations)
        self.assertIn("cost_growth_exceeds_ratio", violations)
        self.assertIn("observed_at_must_not_be_in_the_future", violations)

    def test_invalid_policy_and_naive_clock_fail(self):
        with self.assertRaises(ValueError):
            cost_anomaly_violations({}, {"daily_cap_usd": 0, "maximum_growth_ratio": 2}, now=NOW)
        with self.assertRaises(ValueError):
            cost_anomaly_violations({}, POLICY, now=datetime(2026, 8, 19, 6, 0))
