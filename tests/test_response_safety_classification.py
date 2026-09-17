from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.response_safety_classification import (
    main,
    response_safety_classification_is_safe,
    response_safety_classification_violations,
)


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "response-safety.example.json"


class ResponseSafetyClassificationGateTests(unittest.TestCase):
    def test_confident_safe_response_passes(self):
        records = [{"response_id": "answer-1", "classification": "safe", "confidence": 0.93, "release": True}]
        self.assertTrue(response_safety_classification_is_safe(records))

    def test_duplicate_low_confidence_and_release_mismatch_fail(self):
        records = [{"response_id": "answer-1", "classification": "safe", "confidence": 0.5, "release": False}, {"response_id": "answer-1", "classification": "blocked", "confidence": 1, "release": True}]
        violations = response_safety_classification_violations(records)
        self.assertIn("record_0:safe_classification_confidence_is_too_low", violations)
        self.assertIn("record_0:release_decision_must_match_classification", violations)
        self.assertIn("record_1:response_id_must_be_unique", violations)
        self.assertIn("record_1:release_decision_must_match_classification", violations)

    def test_unhashable_json_fields_are_reported_without_crashing(self):
        records = [
            {
                "response_id": ["answer-1"],
                "classification": ["safe"],
                "confidence": 0.9,
                "release": False,
            }
        ]

        violations = response_safety_classification_violations(records)

        self.assertIn("record_0:response_id_is_required", violations)
        self.assertIn("record_0:classification_is_invalid", violations)

    def test_example_cli_emits_passing_json_report(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main([str(EXAMPLE), "--minimum-safe-confidence", "0.9"])

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(2, report["record_count"])
        self.assertEqual([], report["violations"])

    def test_cli_distinguishes_policy_rejection_from_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            rejected_path = Path(temp_directory) / "rejected.json"
            rejected_path.write_text(
                json.dumps(
                    [
                        {
                            "response_id": "answer-1",
                            "classification": "safe",
                            "confidence": 0.4,
                            "release": True,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                rejected_exit_code = main([str(rejected_path)])

            invalid_path = Path(temp_directory) / "invalid.json"
            invalid_path.write_text("{}", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                invalid_exit_code = main([str(invalid_path)])

        self.assertEqual(1, rejected_exit_code)
        self.assertEqual("fail", json.loads(output.getvalue())["status"])
        self.assertEqual(2, invalid_exit_code)
        self.assertEqual("error", json.loads(error.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
