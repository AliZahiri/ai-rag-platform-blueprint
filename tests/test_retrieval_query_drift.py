import unittest

from scripts.retrieval_query_drift import query_distribution_drift_violations, query_distribution_is_stable


class RetrievalQueryDistributionDriftTests(unittest.TestCase):
    def test_well_sampled_stable_distribution_passes(self):
        baseline = {"snapshot_id": "week-1", "sample_count": 1000, "distribution": {"lookup": 0.6, "comparison": 0.4}}
        candidate = {"snapshot_id": "week-2", "sample_count": 1200, "distribution": {"lookup": 0.55, "comparison": 0.45}}
        self.assertTrue(query_distribution_is_stable(baseline, candidate))

    def test_large_drift_and_insufficient_samples_fail(self):
        baseline = {"snapshot_id": "week-1", "sample_count": 1000, "distribution": {"lookup": 0.9, "comparison": 0.1}}
        candidate = {"snapshot_id": "week-2", "sample_count": 20, "distribution": {"lookup": 0.2, "comparison": 0.8}}
        violations = query_distribution_drift_violations(baseline, candidate)
        self.assertIn("candidate:sample_count_is_below_minimum", violations)
        self.assertIn("query_distribution_total_variation_exceeds_budget", violations)

    def test_invalid_distribution_and_policy_fail(self):
        invalid = {"snapshot_id": "bad", "sample_count": 100, "distribution": {"lookup": 0.4}}
        violations = query_distribution_drift_violations(invalid, invalid)
        self.assertIn("baseline:distribution_must_sum_to_one", violations)
        with self.assertRaises(ValueError):
            query_distribution_drift_violations({}, {}, maximum_total_variation=1.1)
