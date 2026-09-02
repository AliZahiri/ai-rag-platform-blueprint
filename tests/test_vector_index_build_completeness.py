import unittest
from datetime import datetime, timezone

from scripts.vector_index_build_completeness import vector_index_build_is_complete, vector_index_build_violations


NOW = datetime(2026, 9, 2, 4, 0, tzinfo=timezone.utc)


class VectorIndexBuildCompletenessTests(unittest.TestCase):
    def test_fresh_reconciled_build_passes(self):
        manifest = {"document_count": 20, "chunk_count": 180}
        build = {"indexed_document_count": 20, "indexed_chunk_count": 180, "failed_record_count": 0, "index_digest": "sha256:" + "a" * 64, "completed_at": "2026-09-02T03:30:00Z"}
        self.assertTrue(vector_index_build_is_complete(manifest, build, now=NOW))

    def test_missing_chunks_failures_and_stale_evidence_fail(self):
        manifest = {"document_count": 20, "chunk_count": 180}
        build = {"indexed_document_count": 20, "indexed_chunk_count": 170, "failed_record_count": 10, "index_digest": "bad", "completed_at": "2026-09-01T00:00:00Z"}
        violations = vector_index_build_violations(manifest, build, now=NOW)
        self.assertIn("indexed_chunk_count_does_not_match_manifest", violations)
        self.assertIn("failed_record_count_must_be_zero", violations)
        self.assertIn("index_build_evidence_is_stale_or_future_dated", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            vector_index_build_violations({}, {}, now=NOW, maximum_age_seconds=0)
