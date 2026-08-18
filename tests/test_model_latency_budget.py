import unittest

from scripts.model_latency_budget import model_latency_budget_violations, model_latency_is_within_budget


class ModelLatencyBudgetTests(unittest.TestCase):
    def test_observations_within_budget_pass(self):
        self.assertTrue(model_latency_is_within_budget([{"request_id": "req-1", "latency_seconds": 1.5}]))

    def test_missing_invalid_and_slow_observations_fail(self):
        violations = model_latency_budget_violations([{"request_id": "", "latency_seconds": -1}, {"request_id": "req-2", "latency_seconds": 31}])
        self.assertIn("observation_0:request_id_is_required", violations)
        self.assertIn("observation_0:latency_seconds_must_be_non_negative", violations)
        self.assertIn("observation_1:latency_exceeds_budget", violations)


if __name__ == "__main__":
    unittest.main()
