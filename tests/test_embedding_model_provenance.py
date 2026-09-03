import unittest
from datetime import datetime, timezone

from scripts.embedding_model_provenance import embedding_model_provenance_is_ready, embedding_model_provenance_violations


NOW = datetime(2026, 9, 3, 6, 0, tzinfo=timezone.utc)
POLICY = {"expected_model_id": "text-embedding-3-large", "expected_revision": "2026-08-01", "expected_dimension": 3072, "expected_index_snapshot": "index-2026-09-03", "now": NOW}


class EmbeddingModelProvenanceGateTests(unittest.TestCase):
    def test_fresh_approved_embedding_contract_passes(self):
        evidence = {"model_id": "text-embedding-3-large", "model_revision": "2026-08-01", "embedding_dimension": 3072, "index_snapshot": "index-2026-09-03", "model_sha256": "sha256:" + "a" * 64, "observed_at": "2026-09-03T05:30:00Z"}
        self.assertTrue(embedding_model_provenance_is_ready(evidence, **POLICY))

    def test_unapproved_dimension_digest_and_stale_evidence_fail(self):
        evidence = {"model_id": "other", "model_revision": "latest", "embedding_dimension": 1536, "index_snapshot": "old", "model_sha256": "bad", "observed_at": "2026-08-01T00:00:00Z"}
        violations = embedding_model_provenance_violations(evidence, **POLICY)
        self.assertIn("model_id_does_not_match_expected", violations)
        self.assertIn("embedding_dimension_does_not_match_expected", violations)
        self.assertIn("model_sha256_must_be_a_sha256_digest", violations)
        self.assertIn("embedding_provenance_evidence_is_stale_or_future_dated", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            embedding_model_provenance_violations({}, **{**POLICY, "expected_dimension": 0})
