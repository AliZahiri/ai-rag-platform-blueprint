import unittest

from scripts.rag_evaluation_case_result_coverage import evaluation_case_result_coverage_is_complete, evaluation_case_result_coverage_violations


class RagEvaluationCaseResultCoverageTests(unittest.TestCase):
    def test_every_expected_case_reported_once_passes(self):
        self.assertTrue(evaluation_case_result_coverage_is_complete(["case-1", "case-2"], [{"case_id": "case-1", "status": "passed"}, {"case_id": "case-2", "status": "failed"}]))

    def test_missing_duplicate_and_unexpected_results_fail(self):
        violations = evaluation_case_result_coverage_violations(["case-1", "case-2"], [{"case_id": "case-1", "status": "unknown"}, {"case_id": "case-1", "status": "passed"}, {"case_id": "case-3", "status": "passed"}])
        self.assertIn("expected_cases_are_missing_results", violations)
        self.assertIn("unexpected_case_results_are_present", violations)
        self.assertIn("result_1:case_id_must_be_unique", violations)
