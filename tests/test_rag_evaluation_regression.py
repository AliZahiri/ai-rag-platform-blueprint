from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.rag_evaluation_regression import (
    evaluation_regression_is_acceptable,
    evaluation_regression_violations,
    main,
)


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "rag-evaluation-regression.example.json"


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

    def test_example_cli_emits_passing_json_report(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main([str(EXAMPLE), "--maximum-regression", "0.05"])

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(
            ["groundedness", "citation_precision", "answer_relevance"],
            report["metrics"],
        )
        self.assertEqual([], report["violations"])

    def test_cli_distinguishes_policy_rejection_from_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            rejected_path = Path(temp_directory) / "rejected.json"
            rejected_path.write_text(
                json.dumps(
                    {
                        "baseline": {
                            "groundedness": 0.9,
                            "citation_precision": 0.9,
                            "answer_relevance": 0.9,
                        },
                        "candidate": {
                            "groundedness": 0.5,
                            "citation_precision": 0.9,
                            "answer_relevance": 0.9,
                        },
                    }
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                rejected_exit_code = main(
                    [str(rejected_path), "--maximum-regression", "0.05"]
                )

            invalid_path = Path(temp_directory) / "invalid.json"
            invalid_path.write_text("[]", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                invalid_exit_code = main(
                    [str(invalid_path), "--maximum-regression", "0.05"]
                )

        self.assertEqual(1, rejected_exit_code)
        self.assertEqual("fail", json.loads(output.getvalue())["status"])
        self.assertEqual(2, invalid_exit_code)
        self.assertEqual("error", json.loads(error.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
