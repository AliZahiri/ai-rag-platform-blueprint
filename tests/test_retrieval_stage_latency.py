import unittest

from scripts.retrieval_stage_latency import retrieval_latency_is_within_budget, retrieval_latency_violations


class RetrievalStageLatencyBudgetTests(unittest.TestCase):
    def test_complete_observations_within_stage_and_total_budgets_pass(self):
        self.assertTrue(retrieval_latency_is_within_budget({"embed": 20, "search": 35, "rerank": 15}, required_stages=("embed", "search", "rerank"), maximum_total_ms=100, stage_budgets_ms={"search": 50}))

    def test_missing_unknown_stage_and_budget_overruns_fail(self):
        violations = retrieval_latency_violations({"embed": 60, "search": 70, "unknown": 1}, required_stages=("embed", "search", "rerank"), maximum_total_ms=100, stage_budgets_ms={"search": 50})
        self.assertIn("unexpected_retrieval_stage_observed", violations)
        self.assertIn("stage:rerank:latency_must_be_finite_and_non_negative", violations)
        self.assertIn("stage:search:latency_exceeds_budget", violations)
        self.assertIn("total_retrieval_latency_exceeds_budget", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            retrieval_latency_violations({}, required_stages=("search", "search"), maximum_total_ms=10)


if __name__ == "__main__":
    unittest.main()
