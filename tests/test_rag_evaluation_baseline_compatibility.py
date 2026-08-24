import unittest

from scripts.rag_evaluation_baseline_compatibility import baseline_compatibility_violations, evaluation_baseline_is_compatible


class RagEvaluationBaselineCompatibilityTests(unittest.TestCase):
    def test_matching_well_sampled_snapshots_pass(self):
        baseline = {"dataset_sha256": "a" * 64, "scorer_version": "2.1.0", "sample_count": 100, "metrics": ["faithfulness", "recall"]}
        self.assertTrue(evaluation_baseline_is_compatible(dict(baseline), baseline))

    def test_incompatible_or_under_sampled_snapshot_fails(self):
        candidate = {"dataset_sha256": "bad", "scorer_version": "3.0.0", "sample_count": 10, "metrics": ["faithfulness"]}
        baseline = {"dataset_sha256": "a" * 64, "scorer_version": "2.1.0", "sample_count": 100, "metrics": ["faithfulness", "recall"]}
        violations = baseline_compatibility_violations(candidate, baseline)
        self.assertIn("dataset_sha256_must_match_baseline", violations)
        self.assertIn("scorer_version_must_match_baseline", violations)
        self.assertIn("candidate_sample_count_is_below_minimum", violations)
        self.assertIn("metric_set_must_match_baseline", violations)
