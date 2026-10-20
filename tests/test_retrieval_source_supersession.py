import unittest
from datetime import datetime, timezone
from scripts.validate_retrieval_source_supersession import retrieval_source_supersession_violations
NOW=datetime(2026,10,19,12,tzinfo=timezone.utc)
class RetrievalSourceSupersessionTests(unittest.TestCase):
    def test_approved_inactive_superseded_source_passes(self):
        record={'source_id':'docs/v1','successor_source_id':'docs/v2','approval_reference':'RAG-18','effective_at':'2026-10-01T00:00:00Z','source_is_active':False}
        self.assertEqual((), retrieval_source_supersession_violations([record], now=NOW))
    def test_self_active_and_unapproved_record_fails(self):
        record={'source_id':'docs/v1','successor_source_id':'docs/v1','approval_reference':'','effective_at':'2026-10-01T00:00:00Z','source_is_active':True}
        violations=retrieval_source_supersession_violations([record], now=NOW)
        self.assertIn('record_0:successor_source_id_must_be_distinct', violations); self.assertIn('record_0:approval_reference_is_required', violations); self.assertIn('record_0:superseded_source_must_not_remain_active', violations)
