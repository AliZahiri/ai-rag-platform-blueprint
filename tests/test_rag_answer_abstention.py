import unittest

from scripts.rag_answer_abstention import answer_decision_is_safe, answer_decision_violations


class RagAnswerAbstentionEvidenceTests(unittest.TestCase):
    def test_grounded_answer_with_citation_passes(self):
        evidence = {"query_id": "q-42", "decision": "answer", "retrieval_confidence": 0.82, "groundedness": 0.91, "citation_count": 3}
        self.assertTrue(answer_decision_is_safe(evidence))

    def test_explicit_explained_abstention_passes(self):
        evidence = {"query_id": "q-43", "decision": "abstain", "retrieval_confidence": 0.2, "groundedness": 0.3, "citation_count": 0, "reason": "insufficient retrieval evidence"}
        self.assertTrue(answer_decision_is_safe(evidence))

    def test_unsupported_answer_and_unexplained_abstention_fail(self):
        unsupported = {"query_id": "q-44", "decision": "answer", "retrieval_confidence": 0.4, "groundedness": 0.5, "citation_count": 0}
        violations = answer_decision_violations(unsupported)
        self.assertIn("answer_retrieval_confidence_is_below_policy", violations)
        self.assertIn("answer_groundedness_is_below_policy", violations)
        self.assertIn("answer_requires_at_least_one_citation", violations)
        abstention = {**unsupported, "decision": "abstain"}
        self.assertIn("abstention_reason_is_required", answer_decision_violations(abstention))

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            answer_decision_violations({}, minimum_groundedness=float("nan"))
