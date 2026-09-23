from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.retrieval_prompt_injection import (
    main,
    retrieval_context_is_injection_safe,
    retrieval_prompt_injection_violations,
)


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "retrieval-prompt-injection.example.json"


class RetrievalPromptInjectionEvidenceGateTests(unittest.TestCase):
    def test_clean_chunk_and_quarantined_untrusted_signal_pass(self):
        chunks = [{"chunk_id": "safe", "trust_level": "trusted", "instruction_signal_count": 0, "eligible_for_context": True}, {"chunk_id": "risk", "trust_level": "untrusted", "instruction_signal_count": 2, "quarantined": True, "eligible_for_context": False}]
        self.assertTrue(retrieval_context_is_injection_safe(chunks))

    def test_duplicate_untrusted_signal_without_containment_fails(self):
        chunks = [{"chunk_id": "risk", "trust_level": "untrusted", "instruction_signal_count": 1, "quarantined": False, "eligible_for_context": True}, {"chunk_id": "risk", "trust_level": "unknown", "instruction_signal_count": -1}]
        violations = retrieval_prompt_injection_violations(chunks)
        self.assertIn("chunk_0:untrusted_instruction_signals_require_quarantine", violations)
        self.assertIn("chunk_0:quarantined_chunk_must_be_excluded_from_context", violations)
        self.assertIn("chunk_1:chunk_id_must_be_unique", violations)
        self.assertIn("chunk_1:trust_level_is_invalid", violations)
        self.assertIn("chunk_1:instruction_signal_count_must_be_non_negative", violations)

    def test_empty_chunk_set_fails(self):
        self.assertEqual(("at_least_one_retrieval_chunk_is_required",), retrieval_prompt_injection_violations([]))

    def test_example_cli_emits_passing_json_report(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main([str(EXAMPLE)])

        report = json.loads(output.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(2, report["chunk_count"])
        self.assertEqual([], report["violations"])

    def test_cli_distinguishes_policy_rejection_from_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            temp_path = Path(temp_directory)
            rejected_path = temp_path / "rejected.json"
            rejected_path.write_text(
                json.dumps(
                    {
                        "chunks": [
                            {
                                "chunk_id": "uncontained",
                                "trust_level": "untrusted",
                                "instruction_signal_count": 1,
                                "quarantined": False,
                                "eligible_for_context": True,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                rejected_exit_code = main([str(rejected_path)])

            invalid_path = temp_path / "invalid.json"
            invalid_path.write_text("[]", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                invalid_exit_code = main([str(invalid_path)])

        self.assertEqual(1, rejected_exit_code)
        self.assertEqual("fail", json.loads(output.getvalue())["status"])
        self.assertEqual(2, invalid_exit_code)
        self.assertEqual("error", json.loads(error.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
