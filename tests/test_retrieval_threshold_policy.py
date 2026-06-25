import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/retrieval_threshold_policy.py"
SPEC = importlib.util.spec_from_file_location("retrieval_threshold_policy", SCRIPT_PATH)
retrieval_threshold_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retrieval_threshold_policy)


class RetrievalThresholdPolicyTests(unittest.TestCase):
    def test_valid_policy_passes(self):
        policy = {
            "min_similarity_score": 0.72,
            "max_chunks": 8,
            "empty_retrieval_behavior": "ask_clarifying_question",
        }

        self.assertTrue(retrieval_threshold_policy.retrieval_policy_is_safe(policy))

    def test_invalid_policy_reports_warnings(self):
        warnings = retrieval_threshold_policy.retrieval_policy_warnings({"min_similarity_score": 2, "max_chunks": 0})

        self.assertIn("min_similarity_score_must_be_between_0_and_1", warnings)
        self.assertIn("max_chunks_must_be_between_1_and_20", warnings)
        self.assertIn("empty_retrieval_behavior_must_be_explicit", warnings)


if __name__ == "__main__":
    unittest.main()
