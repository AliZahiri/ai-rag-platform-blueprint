import unittest

from scripts.retrieval_confidence import low_confidence_source_ids, retrieval_meets_confidence_threshold


class RetrievalConfidenceTests(unittest.TestCase):
    def test_confident_results_pass(self):
        self.assertTrue(retrieval_meets_confidence_threshold([{"source_id": "law-1", "score": 0.91}], minimum_score=0.8))

    def test_low_confidence_source_is_reported(self):
        self.assertEqual(("law-1",), low_confidence_source_ids([{"source_id": "law-1", "score": 0.2}], minimum_score=0.8))

    def test_non_finite_and_boolean_scores_are_reported(self):
        results = [
            {"source_id": "boolean", "score": True},
            {"source_id": "nan", "score": float("nan")},
            {"source_id": "infinity", "score": float("inf")},
        ]

        self.assertEqual(
            ("boolean", "nan", "infinity"),
            low_confidence_source_ids(results, minimum_score=0.8),
        )

    def test_invalid_minimum_score_is_rejected(self):
        for minimum_score in (True, float("nan"), float("inf")):
            with self.subTest(minimum_score=minimum_score):
                with self.assertRaisesRegex(ValueError, "between 0 and 1"):
                    low_confidence_source_ids([], minimum_score=minimum_score)


if __name__ == "__main__":
    unittest.main()
