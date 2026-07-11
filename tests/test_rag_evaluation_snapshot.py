import unittest

from scripts.rag_evaluation_snapshot import snapshot_passes, snapshot_warnings


class RagEvaluationSnapshotTests(unittest.TestCase):
    def test_complete_snapshot_passes(self):
        snapshot = {
            "question_id": "q-001",
            "retrieved_sources": 3,
            "has_citation": True,
            "freshness_ok": True,
            "review_passed": True,
        }

        self.assertTrue(snapshot_passes(snapshot))

    def test_weak_snapshot_reports_actionable_warnings(self):
        warnings = snapshot_warnings({"question_id": "q-002", "retrieved_sources": 1})

        self.assertIn("retrieved_sources_below_threshold", warnings)
        self.assertIn("answer_missing_citation", warnings)
        self.assertIn("review_passed_is_required", warnings)


if __name__ == "__main__":
    unittest.main()
