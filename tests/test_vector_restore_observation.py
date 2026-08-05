import unittest
from datetime import datetime, timezone

from scripts.vector_restore_observation import vector_restore_violations


NOW = datetime(2026, 8, 5, tzinfo=timezone.utc)
DIGEST = "a" * 64


class VectorRestoreObservationGateTests(unittest.TestCase):
    def test_complete_fresh_queryable_restore_passes(self):
        observation = {"expected_record_count": 100, "restored_record_count": 100, "expected_dimension": 768, "restored_dimension": 768, "expected_manifest_sha256": DIGEST, "restored_manifest_sha256": DIGEST, "sample_query_passed": True, "verified_at": "2026-08-04T23:00:00Z"}
        self.assertEqual((), vector_restore_violations(observation, now=NOW))

    def test_incomplete_mismatched_unqueryable_stale_restore_fails(self):
        observation = {"expected_record_count": 100, "restored_record_count": 99, "expected_dimension": 768, "restored_dimension": 384, "expected_manifest_sha256": DIGEST, "restored_manifest_sha256": "b" * 64, "sample_query_passed": False, "verified_at": "2026-08-01T00:00:00Z"}
        violations = vector_restore_violations(observation, now=NOW)
        self.assertIn("restored_record_count_mismatch", violations)
        self.assertIn("restored_dimension_mismatch", violations)
        self.assertIn("restored_manifest_sha256_mismatch", violations)
        self.assertIn("sample_similarity_query_must_pass", violations)
        self.assertIn("restore_verification_is_not_fresh", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            vector_restore_violations({}, now=NOW, maximum_age_seconds=0)


if __name__ == "__main__":
    unittest.main()
