import unittest

from scripts.rag_evaluation_decision_record import decision_record_is_ready, decision_record_violations


class RagEvaluationDecisionRecordTests(unittest.TestCase):
    def test_distinct_reviewed_record_within_budget_passes(self):
        record = {"release_id": "release-42", "baseline_id": "baseline-41", "candidate_id": "candidate-42", "decision": "approve", "reviewer_ids": ["reviewer-a", "reviewer-b"], "metrics": [{"delta": -0.01, "maximum_regression": 0.02}]}
        self.assertTrue(decision_record_is_ready(record))

    def test_duplicate_reviewers_and_excessive_regression_fail(self):
        record = {"release_id": "release-42", "baseline_id": "same", "candidate_id": "same", "decision": "hold", "reviewer_ids": ["reviewer-a", "reviewer-a"], "metrics": [{"delta": -0.10, "maximum_regression": 0.02}]}
        violations = decision_record_violations(record)
        self.assertIn("baseline_and_candidate_must_differ", violations)
        self.assertIn("decision_must_be_approve_or_reject", violations)
        self.assertIn("reviewer_ids_must_be_unique_non_empty_strings", violations)
        self.assertIn("metric_0_exceeds_regression_budget", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            decision_record_violations({}, minimum_reviewer_count=0)
