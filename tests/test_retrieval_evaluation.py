from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.retrieval_evaluation import main, retrieval_evaluation_report


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "retrieval-evaluation.example.json"


class RetrievalEvaluationTests(unittest.TestCase):
    def test_ranked_evidence_calculates_recall_and_mrr(self):
        report = retrieval_evaluation_report(
            [
                {
                    "case_id": "first",
                    "relevant_source_ids": ["a", "b"],
                    "retrieved_source_ids": ["a", "unrelated", "b"],
                },
                {
                    "case_id": "second",
                    "relevant_source_ids": ["c"],
                    "retrieved_source_ids": ["unrelated", "c"],
                },
            ],
            top_k=2,
            minimum_recall_at_k=0.7,
            minimum_mrr_at_k=0.7,
        )

        self.assertEqual("pass", report["status"])
        self.assertEqual([], report["failed_case_ids"])
        self.assertEqual(0.75, report["metrics"]["mean_recall_at_k"])
        self.assertEqual(0.75, report["metrics"]["mean_mrr_at_k"])

    def test_low_quality_evidence_returns_all_threshold_violations(self):
        report = retrieval_evaluation_report(
            [
                {
                    "case_id": "missed",
                    "relevant_source_ids": ["a"],
                    "retrieved_source_ids": ["unrelated"],
                }
            ],
            top_k=1,
            minimum_recall_at_k=0.8,
            minimum_mrr_at_k=0.8,
        )

        self.assertEqual("fail", report["status"])
        self.assertEqual(["missed"], report["failed_case_ids"])
        self.assertEqual(
            ["mean_recall_at_k_below_minimum", "mean_mrr_at_k_below_minimum"],
            report["violations"],
        )

    def test_invalid_case_shape_duplicate_sources_and_policy_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "only case_id"):
            retrieval_evaluation_report(
                [{"case_id": "case", "relevant_source_ids": ["a"], "retrieved_source_ids": [], "extra": True}],
                top_k=1,
                minimum_recall_at_k=0.5,
                minimum_mrr_at_k=0.5,
            )
        with self.assertRaisesRegex(ValueError, "duplicate source IDs"):
            retrieval_evaluation_report(
                [{"case_id": "case", "relevant_source_ids": ["a"], "retrieved_source_ids": ["a", "a"]}],
                top_k=1,
                minimum_recall_at_k=0.5,
                minimum_mrr_at_k=0.5,
            )
        with self.assertRaisesRegex(ValueError, "top_k"):
            retrieval_evaluation_report([], top_k=False, minimum_recall_at_k=0.5, minimum_mrr_at_k=0.5)

    def test_example_cli_emits_machine_readable_pass_report(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    str(EXAMPLE),
                    "--top-k",
                    "3",
                    "--minimum-recall-at-k",
                    "0.8",
                    "--minimum-mrr-at-k",
                    "0.8",
                ]
            )

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(3, report["case_count"])

    def test_cli_distinguishes_rejection_from_invalid_evidence(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            rejected = Path(temp_directory) / "rejected.json"
            rejected.write_text(
                json.dumps(
                    {"cases": [{"case_id": "missed", "relevant_source_ids": ["a"], "retrieved_source_ids": []}]}
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                rejected_exit_code = main(
                    [str(rejected), "--top-k", "1", "--minimum-recall-at-k", "0.5", "--minimum-mrr-at-k", "0.5"]
                )

            invalid = Path(temp_directory) / "invalid.json"
            invalid.write_text("[]", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                invalid_exit_code = main(
                    [str(invalid), "--top-k", "1", "--minimum-recall-at-k", "0.5", "--minimum-mrr-at-k", "0.5"]
                )

        self.assertEqual(1, rejected_exit_code)
        self.assertEqual("fail", json.loads(output.getvalue())["status"])
        self.assertEqual(2, invalid_exit_code)
        self.assertEqual("error", json.loads(error.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
