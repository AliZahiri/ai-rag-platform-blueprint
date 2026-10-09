import unittest

from scripts.rag_evaluation_metric_contract import (
    evaluation_metric_contract_is_valid,
    evaluation_metric_contract_violations,
)


class EvaluationMetricContractTests(unittest.TestCase):
    def test_valid_directional_contracts_pass(self):
        metrics = [
            {
                "metric_id": "groundedness",
                "direction": "higher_is_better",
                "baseline": 0.8,
                "candidate": 0.79,
                "maximum_regression": 0.01,
            },
            {
                "metric_id": "p95_latency_ms",
                "direction": "lower_is_better",
                "baseline": 240,
                "candidate": 250,
                "maximum_regression": 10,
            },
        ]

        self.assertTrue(evaluation_metric_contract_is_valid(metrics))

    def test_regressions_beyond_directional_budget_fail(self):
        violations = evaluation_metric_contract_violations(
            [
                {
                    "metric_id": "answer_relevance",
                    "direction": "higher_is_better",
                    "baseline": 0.9,
                    "candidate": 0.87,
                    "maximum_regression": 0.02,
                },
                {
                    "metric_id": "cost_usd",
                    "direction": "lower_is_better",
                    "baseline": 0.04,
                    "candidate": 0.06,
                    "maximum_regression": 0.01,
                },
            ]
        )

        self.assertEqual(
            ("metric_0:regression_exceeds_maximum", "metric_1:regression_exceeds_maximum"),
            violations,
        )

    def test_malformed_identifiers_and_numeric_values_fail(self):
        violations = evaluation_metric_contract_violations(
            [
                {
                    "metric_id": "Groundedness",
                    "direction": "sideways",
                    "baseline": float("nan"),
                    "candidate": True,
                    "maximum_regression": -1,
                },
                {
                    "metric_id": "Groundedness",
                    "direction": "lower_is_better",
                    "baseline": 1,
                    "candidate": float("inf"),
                    "maximum_regression": 0,
                },
            ]
        )

        self.assertEqual(
            (
                "metric_0:metric_id_must_be_a_stable_identifier",
                "metric_0:direction_is_invalid",
                "metric_0:baseline_must_be_a_finite_number",
                "metric_0:candidate_must_be_a_finite_number",
                "metric_0:maximum_regression_must_be_non_negative",
                "metric_1:metric_id_must_be_a_stable_identifier",
                "metric_1:candidate_must_be_a_finite_number",
            ),
            violations,
        )

    def test_empty_or_non_list_contract_fails(self):
        self.assertEqual(
            ("at_least_one_metric_is_required",),
            evaluation_metric_contract_violations({}),
        )


if __name__ == "__main__":
    unittest.main()
