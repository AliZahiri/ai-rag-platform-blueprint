import unittest

from scripts.rag_evaluation_release_evidence import evaluation_release_evidence_violations, evaluation_release_is_ready


class RagEvaluationReleaseEvidenceGateTests(unittest.TestCase):
    def test_complete_release_evidence_passes(self):
        evidence = {"evaluation_id": "eval-2026-08", "dataset_version": "v4", "metrics": {"groundedness": 0.95, "answer_relevance": 0.91}, "thresholds": {"groundedness": 0.9, "answer_relevance": 0.9}, "evaluated_at": "2026-08-20T12:00:00Z", "regression_reviewed": True}
        self.assertTrue(evaluation_release_is_ready(evidence))

    def test_missing_and_below_threshold_controls_are_reported(self):
        violations = evaluation_release_evidence_violations({"evaluation_id": "", "dataset_version": "", "metrics": {"groundedness": 0.8, "answer_relevance": 2}, "thresholds": {"groundedness": 0.9, "answer_relevance": 0.9}, "evaluated_at": "2026-08-20T12:00:00", "regression_reviewed": False})
        self.assertEqual(violations, ("evaluation_id_is_required", "dataset_version_is_required", "groundedness_is_below_release_threshold", "answer_relevance_must_be_a_probability", "evaluated_at_must_be_timezone_aware", "regression_review_must_pass"))
