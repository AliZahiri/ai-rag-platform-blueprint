import unittest

from scripts.retrieval_confidence import low_confidence_source_ids, retrieval_meets_confidence_threshold


class RetrievalConfidenceTests(unittest.TestCase):
    def test_confident_results_pass(self):
        self.assertTrue(retrieval_meets_confidence_threshold([{"source_id": "law-1", "score": 0.91}], minimum_score=0.8))

    def test_low_confidence_source_is_reported(self):
        self.assertEqual(("law-1",), low_confidence_source_ids([{"source_id": "law-1", "score": 0.2}], minimum_score=0.8))


if __name__ == "__main__":
    unittest.main()
