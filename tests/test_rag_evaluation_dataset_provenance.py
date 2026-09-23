from datetime import datetime, timezone
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.rag_evaluation_dataset_provenance import (
    evaluation_dataset_provenance_is_complete,
    evaluation_dataset_provenance_violations,
    main,
)


NOW = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "rag-evaluation-provenance.example.json"


class RagEvaluationDatasetProvenanceGateTests(unittest.TestCase):
    def test_reviewed_traceable_case_passes(self):
        cases = [{"case_id": "support-001", "source_snapshot": "knowledge-2026-08-01", "expected_answer": "Reset the documented token.", "source_ids": ["handbook-1"], "reviewed_at": "2026-08-01T10:00:00Z"}]
        self.assertTrue(evaluation_dataset_provenance_is_complete(cases, now=NOW))

    def test_duplicate_incomplete_and_stale_cases_fail(self):
        cases = [{"case_id": "support-001", "source_snapshot": "", "expected_answer": "", "source_ids": ["handbook-1", "handbook-1"], "reviewed_at": "2025-01-01T00:00:00Z"}, {"case_id": "support-001", "source_snapshot": "snapshot", "expected_answer": "ok", "source_ids": ["handbook-2"], "reviewed_at": "2026-08-01T10:00:00Z"}]
        violations = evaluation_dataset_provenance_violations(cases, now=NOW)
        self.assertIn("case_0:source_snapshot_is_required", violations)
        self.assertIn("case_0:expected_answer_is_required", violations)
        self.assertIn("case_0:source_ids_must_be_a_unique_non_empty_string_list", violations)
        self.assertIn("case_0:review_is_not_within_age_budget", violations)
        self.assertIn("case_1:case_id_must_be_unique", violations)

    def test_empty_cases_and_invalid_policy_fail(self):
        self.assertEqual(("at_least_one_evaluation_case_is_required",), evaluation_dataset_provenance_violations([], now=NOW))
        with self.assertRaises(ValueError):
            evaluation_dataset_provenance_violations([], now=datetime(2026, 8, 12), maximum_review_age_days=0)

    def test_example_cli_emits_passing_json_report(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [str(EXAMPLE), "--now", "2026-09-05T12:00:00Z"]
            )

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(1, report["case_count"])
        self.assertEqual([], report["violations"])

    def test_cli_distinguishes_policy_rejection_from_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            temp_path = Path(temp_directory)
            rejected_path = temp_path / "rejected.json"
            rejected_path.write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "case_id": "stale",
                                "source_snapshot": "snapshot",
                                "expected_answer": "answer",
                                "source_ids": ["source"],
                                "reviewed_at": "2025-01-01T00:00:00Z",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                rejected_exit_code = main(
                    [str(rejected_path), "--now", "2026-09-05T12:00:00Z"]
                )

            invalid_path = temp_path / "invalid.json"
            invalid_path.write_text("[]", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                invalid_exit_code = main(
                    [str(invalid_path), "--now", "2026-09-05T12:00:00Z"]
                )

        self.assertEqual(1, rejected_exit_code)
        self.assertEqual("fail", json.loads(output.getvalue())["status"])
        self.assertEqual(2, invalid_exit_code)
        self.assertEqual("error", json.loads(error.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
