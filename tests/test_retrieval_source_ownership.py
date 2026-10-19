import unittest
from datetime import datetime, timezone
from scripts.validate_retrieval_source_ownership import retrieval_source_ownership_violations
NOW = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
class RetrievalSourceOwnershipTests(unittest.TestCase):
    def test_owned_recent_source_passes(self):
        source = {'source_id':'handbook/api','owner':'platform','authority':'internal','reviewed_at':'2026-09-20T12:00:00Z'}
        self.assertEqual((), retrieval_source_ownership_violations([source], now=NOW))
    def test_duplicate_unowned_and_stale_source_fails(self):
        source = {'source_id':'handbook/api','owner':'','authority':'unknown','reviewed_at':'2025-01-01T00:00:00Z'}
        violations = retrieval_source_ownership_violations([source, source], now=NOW)
        self.assertIn('source_0:owner_is_required', violations); self.assertIn('source_1:source_id_must_be_unique', violations); self.assertIn('source_0:ownership_review_is_invalid_stale_or_future_dated', violations)
    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError): retrieval_source_ownership_violations([], now=NOW, maximum_review_age_seconds=0)
