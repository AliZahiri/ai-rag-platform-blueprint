import unittest

from scripts.rag_evaluation_leakage import evaluation_holdout_is_isolated, evaluation_leakage_violations


class RagEvaluationLeakageEvidenceTests(unittest.TestCase):
    def test_disjoint_opaque_holdout_passes(self):
        training = [format(index, "032x") for index in range(20)]
        holdout = [format(index, "032x") for index in range(20, 40)]
        self.assertTrue(evaluation_holdout_is_isolated(training, holdout))

    def test_overlap_duplicates_and_small_holdout_fail(self):
        shared = "a" * 32
        violations = evaluation_leakage_violations([shared, shared], [shared], minimum_holdout_size=2)
        self.assertIn("training_ids_must_be_unique", violations)
        self.assertIn("holdout_size_is_below_minimum", violations)
        self.assertIn("training_and_holdout_ids_overlap", violations)

    def test_raw_or_malformed_identifiers_fail(self):
        violations = evaluation_leakage_violations(["customer prompt"], ["bad"], minimum_holdout_size=1)
        self.assertIn("training_ids_must_be_opaque_hex_identifiers", violations)
        self.assertIn("holdout_ids_must_be_opaque_hex_identifiers", violations)
