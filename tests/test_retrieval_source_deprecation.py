import unittest
from datetime import datetime, timezone
from scripts.validate_retrieval_source_deprecation import retrieval_source_deprecation_violations
NOW=datetime(2026,10,19,12,tzinfo=timezone.utc)
class RetrievalSourceDeprecationTests(unittest.TestCase):
    def test_replaced_source_passes(self):
        record={'source_id':'handbook/v1','effective_at':'2026-10-01T00:00:00Z','disposition':'replace','replacement_source_id':'handbook/v2'}
        self.assertEqual((), retrieval_source_deprecation_violations([record], now=NOW))
    def test_future_duplicate_and_missing_replacement_fail(self):
        record={'source_id':'handbook/v1','effective_at':'2026-12-01T00:00:00Z','disposition':'replace'}
        violations=retrieval_source_deprecation_violations([record, record], now=NOW)
        self.assertIn('record_0:effective_at_must_not_be_future_dated', violations); self.assertIn('record_0:replacement_source_id_is_required', violations); self.assertIn('record_1:source_id_must_be_unique', violations)
