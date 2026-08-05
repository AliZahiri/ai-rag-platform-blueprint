import unittest

from scripts.retrieval_prompt_injection import retrieval_context_is_injection_safe, retrieval_prompt_injection_violations


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


if __name__ == "__main__":
    unittest.main()
