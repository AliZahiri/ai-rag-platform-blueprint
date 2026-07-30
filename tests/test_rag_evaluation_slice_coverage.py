import unittest

from scripts.rag_evaluation_slice_coverage import evaluation_slice_coverage_is_sufficient, evaluation_slice_coverage_violations


class RagEvaluationSliceCoverageTests(unittest.TestCase):
    def test_unique_samples_covering_every_required_slice_pass(self):
        samples = [{"sample_id": "q-1", "slice": "long-context"}, {"sample_id": "q-2", "slice": "multilingual"}]
        self.assertTrue(evaluation_slice_coverage_is_sufficient(samples=samples, required_slices=("long-context", "multilingual")))

    def test_missing_slice_duplicate_id_and_unknown_slice_are_reported(self):
        samples = [{"sample_id": "q-1", "slice": "long-context"}, {"sample_id": "q-1", "slice": "unplanned"}]
        violations = evaluation_slice_coverage_violations(samples, required_slices=("long-context", "multilingual"))
        self.assertIn("sample_1:sample_id_must_be_unique", violations)
        self.assertIn("sample_1:slice_is_not_declared", violations)
        self.assertIn("slice:multilingual:samples_below_minimum", violations)

    def test_invalid_policy_and_incomplete_sample_metadata_fail(self):
        violations = evaluation_slice_coverage_violations([{"sample_id": "", "slice": ""}], required_slices=("core",))
        self.assertIn("sample_0:sample_id_is_required", violations)
        self.assertIn("sample_0:slice_is_required", violations)
        with self.assertRaises(ValueError):
            evaluation_slice_coverage_violations([], required_slices=("core",), minimum_samples_per_slice=0)


if __name__ == "__main__":
    unittest.main()
