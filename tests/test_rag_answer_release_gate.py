import unittest

from scripts.rag_answer_release_gate import answer_is_releasable, answer_release_violations


class RagAnswerReleaseGateTests(unittest.TestCase):
    def test_confident_diverse_fully_grounded_answer_passes(self):
        results = [{"source_id": "s1", "source_url": "https://one.example/a", "score": 0.9}, {"source_id": "s2", "source_url": "https://two.example/b", "score": 0.85}]
        self.assertTrue(answer_is_releasable(results=results, claim_ids=["c1"], evidence_by_claim={"c1": ["s1"]}, minimum_score=0.8, minimum_domains=2))

    def test_quality_failures_are_reported_together(self):
        results = [{"source_id": "s1", "source_url": "https://one.example/a", "score": 0.2}]
        violations = answer_release_violations(results=results, claim_ids=["c1"], evidence_by_claim={}, minimum_score=0.8, minimum_domains=2)
        self.assertIn("retrieval_confidence_gate_failed:s1", violations)
        self.assertIn("evidence_coverage_gate_failed:c1", violations)
        self.assertIn("retrieval_domain_diversity_gate_failed", violations)


if __name__ == "__main__":
    unittest.main()
