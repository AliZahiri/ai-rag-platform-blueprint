import unittest

from scripts.retrieval_deletion_propagation import deletion_has_propagated, deletion_propagation_violations


class RetrievalDeletionPropagationTests(unittest.TestCase):
    def evidence(self):
        acknowledgements = {name: {"deleted_source_ids": ["source-1"], "completed_at": "2026-09-01T00:05:00Z"} for name in ("vector_index", "retrieval_cache", "serving_layer")}
        return {"request_id": "delete-1", "source_ids": ["source-1"], "requested_at": "2026-09-01T00:00:00Z", "store_acknowledgements": acknowledgements, "residual_source_ids": []}

    def test_complete_bounded_propagation_passes(self):
        self.assertTrue(deletion_has_propagated(self.evidence()))

    def test_missing_store_late_acknowledgement_and_residual_hit_fail(self):
        evidence = self.evidence()
        del evidence["store_acknowledgements"]["retrieval_cache"]
        evidence["store_acknowledgements"]["vector_index"]["completed_at"] = "2026-09-01T01:00:00Z"
        evidence["residual_source_ids"] = ["source-1"]
        violations = deletion_propagation_violations(evidence)
        self.assertIn("retrieval_cache:acknowledgement_is_required", violations)
        self.assertIn("vector_index:propagation_budget_exceeded", violations)
        self.assertIn("deleted_sources_remain_retrievable", violations)

    def test_invalid_policy_and_naive_request_time_fail(self):
        evidence = self.evidence()
        evidence["requested_at"] = "2026-09-01T00:00:00"
        self.assertIn("requested_at_must_be_timezone_aware", deletion_propagation_violations(evidence))
        with self.assertRaises(ValueError):
            deletion_propagation_violations(evidence, maximum_propagation_seconds=0)
