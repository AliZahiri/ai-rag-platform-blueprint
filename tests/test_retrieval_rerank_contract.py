import unittest

from scripts.retrieval_rerank_contract import retrieval_rerank_is_valid, retrieval_rerank_violations


class RetrievalRerankResultContractGateTests(unittest.TestCase):
    def test_unique_ranked_candidates_above_threshold_pass(self):
        candidates = [{"chunk_id": "a"}, {"chunk_id": "b"}]
        results = [{"chunk_id": "b", "rank": 1, "score": 0.9}, {"chunk_id": "a", "rank": 2, "score": 0.7}]
        self.assertTrue(retrieval_rerank_is_valid(candidates, results, minimum_score=0.5))

    def test_unknown_duplicate_weak_and_misordered_results_fail(self):
        candidates = [{"chunk_id": "a"}, {"chunk_id": "b"}]
        results = [{"chunk_id": "a", "rank": 2, "score": 0.4}, {"chunk_id": "missing", "rank": 2, "score": 0.8}, {"chunk_id": "a", "rank": 3, "score": 0.3}]
        violations = retrieval_rerank_violations(candidates, results, minimum_score=0.5, maximum_results=3)
        self.assertIn("rerank_result_count_exceeds_limit", violations)
        self.assertIn("result_0:rank_must_be_contiguous", violations)
        self.assertIn("result_0:score_below_minimum", violations)
        self.assertIn("result_1:chunk_id_is_not_a_candidate", violations)
        self.assertIn("result_1:score_order_is_not_descending", violations)
        self.assertIn("result_2:chunk_id_must_be_unique", violations)

    def test_empty_candidates_and_invalid_policy_fail(self):
        self.assertEqual(("at_least_one_candidate_is_required",), retrieval_rerank_violations([], []))
        with self.assertRaises(ValueError):
            retrieval_rerank_violations([{},], [], maximum_results=0)


if __name__ == "__main__":
    unittest.main()
