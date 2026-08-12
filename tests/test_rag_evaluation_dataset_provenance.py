import unittest
from datetime import datetime, timezone

from scripts.rag_evaluation_dataset_provenance import evaluation_dataset_provenance_is_complete, evaluation_dataset_provenance_violations


NOW = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)


class RagEvaluationDatasetProvenanceGateTests(unittest.TestCase):
    def test_reviewed_traceable_case_passes(self):
        cases = [{"case_id": "support-001", "source_snapshot": "knowledge-2026-08-01", "expected_answer": "Reset the documented token.", "source_ids": ["handbook-1"], "reviewed_at": "2026-08-01T10:00:00Z"}]
        self.assertTrue(evaluation_dataset_provenance_is_complete(cases, now=NOW))

    def test_duplicate_incomplete_and_stale_cases_fail(self):
        cases = [{"case_id": "support-001", "source_snapshot": "", "expected_answer": "", "source_ids": ["handbook-1", "handbook-1"], "reviewed_at": "2025-01-01T00:00:00Z"}, {"case_id": "support-001", "source_snapshot": "snapshot", "expected_answer": "ok", "source_ids": ["handbook-2"], "reviewed_at": "2026-08-01T10:00:00Z"}]
        violations = evaluation_dataset_provenance_violations(cases, now=NOW)
        self.assertIn("case_0:source_snapshot_is_required", violations)
        self.assertIn("case_0:expected_answer_is_required", violations)
        self.assertIn("case_0:source_ids_must_be_a_unique_non_empty_string_list", violations)
        self.assertIn("case_0:review_is_not_within_age_budget", violations)
        self.assertIn("case_1:case_id_must_be_unique", violations)

    def test_empty_cases_and_invalid_policy_fail(self):
        self.assertEqual(("at_least_one_evaluation_case_is_required",), evaluation_dataset_provenance_violations([], now=NOW))
        with self.assertRaises(ValueError):
            evaluation_dataset_provenance_violations([], now=datetime(2026, 8, 12), maximum_review_age_days=0)


if __name__ == "__main__":
    unittest.main()
