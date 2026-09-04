import unittest
from datetime import datetime, timezone

from scripts.index_replica_consistency import index_replica_consistency_violations, index_replicas_are_consistent


NOW = datetime(2026, 9, 4, 6, 0, tzinfo=timezone.utc)
DIGEST = "sha256:" + "a" * 64
POLICY = {"expected_generation": "generation-42", "expected_document_count": 1200, "expected_sha256": DIGEST, "now": NOW}


class IndexReplicaConsistencyEvidenceTests(unittest.TestCase):
    def test_two_fresh_matching_replicas_pass(self):
        replicas = [{"replica_id": name, "healthy": True, "index_generation": "generation-42", "document_count": 1200, "index_sha256": DIGEST, "observed_at": "2026-09-04T05:55:00Z"} for name in ("az-a", "az-b")]
        self.assertTrue(index_replicas_are_consistent(replicas, **POLICY))

    def test_stale_and_divergent_replica_fails(self):
        replicas = [{"replica_id": "az-a", "healthy": True, "index_generation": "generation-42", "document_count": 1200, "index_sha256": DIGEST, "observed_at": "2026-09-04T05:55:00Z"}, {"replica_id": "az-b", "healthy": False, "index_generation": "generation-41", "document_count": 1190, "index_sha256": "sha256:" + "b" * 64, "observed_at": "2026-09-04T04:00:00Z"}]
        violations = index_replica_consistency_violations(replicas, **POLICY)
        self.assertIn("replica_1:must_be_healthy", violations)
        self.assertIn("replica_1:generation_mismatch", violations)
        self.assertIn("replica_1:digest_mismatch", violations)
        self.assertIn("replica_1:observation_is_invalid_stale_or_future_dated", violations)

    def test_replica_quorum_and_policy_are_validated(self):
        self.assertEqual(("minimum_index_replica_count_not_met",), index_replica_consistency_violations([], **POLICY))
        with self.assertRaises(ValueError):
            index_replica_consistency_violations([], **{**POLICY, "minimum_replicas": 1})
