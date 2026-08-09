import unittest

from scripts.embedding_migration_readiness import embedding_migration_is_ready, embedding_migration_violations


class EmbeddingMigrationReadinessGateTests(unittest.TestCase):
    def test_backfilled_dual_read_evidence_with_overlap_passes(self):
        evidence = {"source_dimension": 768, "target_dimension": 1024, "sample_count": 50, "top_result_overlap_ratio": 0.9, "dual_write_enabled": True, "backfill_complete": True, "source_query_passed": True, "target_query_passed": True}
        self.assertTrue(embedding_migration_is_ready(evidence))

    def test_incomplete_low_overlap_migration_fails(self):
        evidence = {"source_dimension": 0, "target_dimension": 1024, "sample_count": 5, "top_result_overlap_ratio": 0.4, "dual_write_enabled": False, "backfill_complete": False, "source_query_passed": True, "target_query_passed": False}
        violations = embedding_migration_violations(evidence)
        self.assertIn("source_dimension_must_be_a_positive_integer", violations)
        self.assertIn("sample_count_below_minimum", violations)
        self.assertIn("top_result_overlap_ratio_below_minimum", violations)
        self.assertIn("dual_write_enabled_must_be_true", violations)
        self.assertIn("target_query_passed_must_be_true", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            embedding_migration_violations({}, minimum_overlap_ratio=1.1)


if __name__ == "__main__":
    unittest.main()
