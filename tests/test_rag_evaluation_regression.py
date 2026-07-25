import unittest

from scripts.rag_evaluation_regression import evaluation_regression_is_acceptable, evaluation_regression_violations


class RagEvaluationRegressionTests(unittest.TestCase):
    def test_candidate_within_regression_budget_passes(self):
        baseline = {"groundedness": 0.90, "citation_precision": 0.85, "answer_relevance": 0.88}
        candidate = {"groundedness": 0.87, "citation_precision": 0.86, "answer_relevance": 0.84}

        self.assertTrue(evaluation_regression_is_acceptable(baseline=baseline, candidate=candidate, maximum_regression=0.05))

    def test_multiple_quality_regressions_are_reported(self):
        baseline = {"groundedness": 0.90, "citation_precision": 0.90, "answer_relevance": 0.90}
        candidate = {"groundedness": 0.70, "citation_precision": 0.89, "answer_relevance": 0.60}

        violations = evaluation_regression_violations(baseline=baseline, candidate=candidate, maximum_regression=0.05)

        self.assertIn("groundedness:regression_exceeds_budget", violations)
        self.assertIn("answer_relevance:regression_exceeds_budget", violations)

    def test_missing_non_finite_and_invalid_budget_values_fail(self):
        baseline = {"groundedness": 0.9, "citation_precision": 0.9, "answer_relevance": 0.9}
        candidate = {"groundedness": float("nan"), "citation_precision": 0.9}
        violations = evaluation_regression_violations(baseline=baseline, candidate=candidate, maximum_regression=0.05)
        self.assertIn("candidate:groundedness:score_must_be_between_zero_and_one", violations)
        self.assertIn("candidate:answer_relevance:score_must_be_between_zero_and_one", violations)
        with self.assertRaises(ValueError):
            evaluation_regression_violations(baseline=baseline, candidate=baseline, maximum_regression=-0.1)


if __name__ == "__main__":
    unittest.main()
