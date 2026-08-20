import unittest
from datetime import date

from scripts.rag_evaluation_privacy import evaluation_privacy_is_approved, evaluation_privacy_violations


class RagEvaluationPrivacyEvidenceGateTests(unittest.TestCase):
    def test_recent_approved_privacy_evidence_passes(self):
        evidence = {"dataset_id": "eval-2026-08", "approved_by": "privacy-reviewer", "pii_scan_passed": True, "redaction_verified": True, "reviewed_at": "2026-08-01"}
        self.assertTrue(evaluation_privacy_is_approved(evidence, today=date(2026, 8, 20)))

    def test_missing_controls_and_stale_review_are_reported(self):
        violations = evaluation_privacy_violations({"dataset_id": "", "approved_by": "", "pii_scan_passed": False, "redaction_verified": False, "reviewed_at": "2026-01-01"}, today=date(2026, 8, 20), max_review_age_days=30)
        self.assertEqual(violations, ("dataset_id_is_required", "approved_by_is_required", "pii_scan_must_pass", "redaction_must_be_verified", "privacy_review_is_stale"))

    def test_invalid_policy_and_future_review_fail(self):
        violations = evaluation_privacy_violations({"dataset_id": "eval", "approved_by": "reviewer", "pii_scan_passed": True, "redaction_verified": True, "reviewed_at": "2026-08-21"}, today=date(2026, 8, 20), max_review_age_days=0)
        self.assertEqual(violations, ("max_review_age_days_must_be_positive",))
