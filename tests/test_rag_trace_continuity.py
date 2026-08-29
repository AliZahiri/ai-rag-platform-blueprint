import unittest

from scripts.rag_trace_continuity import rag_trace_is_continuous, trace_continuity_violations


class RagTraceContinuityEvidenceTests(unittest.TestCase):
    def test_complete_parented_trace_passes(self):
        evidence = {"request_id": "req-1", "trace_id": "trace-1", "spans": [{"span_id": "retrieve", "trace_id": "trace-1", "stage": "retrieval", "status": "ok"}, {"span_id": "generate", "parent_span_id": "retrieve", "trace_id": "trace-1", "stage": "generation", "status": "ok"}, {"span_id": "cite", "parent_span_id": "generate", "trace_id": "trace-1", "stage": "citation", "status": "ok"}]}
        self.assertTrue(rag_trace_is_continuous(evidence))

    def test_cross_trace_duplicate_and_broken_parent_fail(self):
        evidence = {"request_id": "req-2", "trace_id": "trace-2", "spans": [{"span_id": "shared", "trace_id": "other", "stage": "retrieval", "status": "error"}, {"span_id": "shared", "parent_span_id": "wrong", "trace_id": "trace-2", "stage": "generation", "status": "ok"}, {"span_id": "cite", "parent_span_id": "wrong", "trace_id": "trace-2", "stage": "citation", "status": "ok"}]}
        violations = trace_continuity_violations(evidence)
        self.assertIn("span_0:trace_id_must_match", violations)
        self.assertIn("span_1:span_id_must_be_unique", violations)
        self.assertIn("generation_must_descend_from_retrieval", violations)
        self.assertIn("citation_must_descend_from_generation", violations)
