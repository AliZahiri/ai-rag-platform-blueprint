import unittest

from scripts.response_safety_classification import response_safety_classification_is_safe, response_safety_classification_violations


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


if __name__ == "__main__":
    unittest.main()
