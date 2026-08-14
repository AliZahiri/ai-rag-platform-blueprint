import unittest
from datetime import datetime, timezone

from scripts.retrieval_indexing_freshness import retrieval_indexing_freshness_violations, retrieval_indexing_is_fresh


NOW = datetime(2026, 8, 14, 6, 0, tzinfo=timezone.utc)
RECORD = {"source_id": "handbook", "content_sha256": "a" * 64, "source_updated_at": "2026-08-14T04:00:00Z", "indexed_at": "2026-08-14T05:00:00Z"}


class RetrievalIndexingFreshnessGateTests(unittest.TestCase):
    def test_recent_indexed_source_passes(self):
        self.assertTrue(retrieval_indexing_is_fresh([RECORD], now=NOW))

    def test_duplicate_invalid_and_stale_records_fail(self):
        stale = {**RECORD, "content_sha256": "bad", "source_updated_at": "2026-08-12T00:00:00Z", "indexed_at": "2026-08-13T00:00:00Z"}
        violations = retrieval_indexing_freshness_violations([stale, RECORD], now=NOW)
        self.assertIn("record_0:content_sha256_is_invalid", violations)
        self.assertIn("record_0:indexing_delay_exceeds_budget", violations)
        self.assertIn("record_0:index_observation_is_not_fresh", violations)
        self.assertIn("record_1:source_id_must_be_unique", violations)

    def test_invalid_policy_and_naive_clock_fail(self):
        with self.assertRaises(ValueError):
            retrieval_indexing_freshness_violations([], now=NOW, maximum_delay_hours=0)
        with self.assertRaises(ValueError):
            retrieval_indexing_freshness_violations([], now=datetime(2026, 8, 14, 6, 0))


if __name__ == "__main__":
    unittest.main()
