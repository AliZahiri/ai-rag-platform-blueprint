import unittest

from scripts.validate_retrieval_source_change_budget import (
    retrieval_source_change_budget_violations,
    retrieval_source_change_is_within_budget,
)


def source(source_id: str, digest: str) -> dict[str, str]:
    return {"source_id": source_id, "content_sha256": f"sha256:{digest * 64}"}


class RetrievalSourceChangeBudgetTests(unittest.TestCase):
    def setUp(self):
        self.baseline = [source("docs/a", "a"), source("docs/b", "b"), source("docs/c", "c"), source("docs/d", "d"), source("docs/e", "e")]

    def test_small_reviewed_change_within_budget_passes(self):
        candidate = [source("docs/a", "f"), *self.baseline[1:]]
        self.assertTrue(retrieval_source_change_is_within_budget(self.baseline, candidate))

    def test_large_change_requires_an_approval_reference(self):
        candidate = [source("docs/a", "f"), source("docs/b", "e"), *self.baseline[2:]]
        violations = retrieval_source_change_budget_violations(self.baseline, candidate)
        self.assertIn("source_change_budget_exceeded_without_approval", violations)
        self.assertEqual((), retrieval_source_change_budget_violations(self.baseline, candidate, approval_reference="RAG-142"))

    def test_duplicate_and_malformed_source_evidence_fails(self):
        candidate = [source("docs/a", "a"), source("docs/a", "b"), {"source_id": "bad id", "content_sha256": "nope"}]
        violations = retrieval_source_change_budget_violations(self.baseline, candidate)
        self.assertIn("candidate_1:source_id_must_be_unique", violations)
        self.assertIn("candidate_2:source_id_is_invalid", violations)

    def test_invalid_budget_fails_fast(self):
        with self.assertRaises(ValueError):
            retrieval_source_change_budget_violations(self.baseline, self.baseline, maximum_changed_fraction=1.1)
