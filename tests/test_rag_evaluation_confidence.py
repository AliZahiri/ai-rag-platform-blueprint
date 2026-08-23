import unittest

from scripts.rag_evaluation_confidence import evaluation_confidence_is_sufficient, evaluation_confidence_violations


class RagEvaluationConfidenceGateTests(unittest.TestCase):
    def test_versioned_well_sampled_lower_bound_passes(self):
        evidence = {"dataset_version": "eval-v7", "sample_count": 500, "confidence_level": 0.95, "score_lower_bound": 0.87, "evaluated_at": "2026-08-23T08:00:00Z"}
        self.assertTrue(evaluation_confidence_is_sufficient(evidence, min_samples=200, min_lower_bound=0.85))

    def test_small_sample_and_weak_lower_bound_fail(self):
        violations = evaluation_confidence_violations({"dataset_version": "", "sample_count": 20, "confidence_level": 0, "score_lower_bound": 0.7, "evaluated_at": "2026-08-23T08:00:00"}, min_samples=100, min_lower_bound=0.8)
        self.assertEqual(violations, ("dataset_version_is_required", "sample_count_is_below_minimum", "confidence_level_must_be_a_positive_probability", "score_lower_bound_is_below_release_threshold", "evaluated_at_must_be_timezone_aware"))

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluation_confidence_violations({}, min_samples=0)
