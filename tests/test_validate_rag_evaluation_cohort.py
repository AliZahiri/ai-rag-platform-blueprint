import unittest
from datetime import datetime, timezone
from scripts.validate_rag_evaluation_cohort import rag_evaluation_violations

NOW = datetime(2026, 9, 13, 12, tzinfo=timezone.utc)
class RagEvaluationCohortTests(unittest.TestCase):
    def test_fresh_complete_evaluation_passes(self):
        evidence = {'dataset_id':'golden-v1','completed':True,'query_count':50,'citation_precision':0.91,'observed_at':'2026-09-13T11:00:00Z'}
        self.assertEqual((), rag_evaluation_violations(evidence, dataset_id='golden-v1', now=NOW))
    def test_wrong_incomplete_small_and_stale_evidence_fails(self):
        evidence = {'dataset_id':'other','completed':False,'query_count':2,'citation_precision':0.2,'observed_at':'2026-09-10T00:00:00Z'}
        violations = rag_evaluation_violations(evidence, dataset_id='golden-v1', now=NOW)
        self.assertIn('evaluation_dataset_must_match_approved_cohort', violations)
        self.assertIn('evaluation_query_count_is_below_minimum', violations)
        self.assertIn('evaluation_evidence_is_invalid_stale_or_future_dated', violations)
    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError): rag_evaluation_violations({}, dataset_id='', now=NOW)
