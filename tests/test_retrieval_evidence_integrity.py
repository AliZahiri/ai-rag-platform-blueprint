import unittest

from scripts.retrieval_evidence_integrity import retrieval_evidence_has_integrity, retrieval_evidence_integrity_violations


DIGEST = "a" * 64


class RetrievalEvidenceIntegrityGateTests(unittest.TestCase):
    def test_unique_evidence_matching_manifest_passes(self):
        self.assertTrue(retrieval_evidence_has_integrity([{"source_id": "doc-1", "content_sha256": DIGEST}], expected_hashes={"doc-1": DIGEST}))

    def test_duplicate_unknown_invalid_and_mismatched_evidence_fail(self):
        records = [{"source_id": "doc-1", "content_sha256": "b" * 64}, {"source_id": "doc-1", "content_sha256": "bad"}, {"source_id": "doc-2", "content_sha256": DIGEST}]
        violations = retrieval_evidence_integrity_violations(records, expected_hashes={"doc-1": DIGEST})
        self.assertIn("record_0:content_sha256_mismatch", violations)
        self.assertIn("record_1:source_id_must_be_unique", violations)
        self.assertIn("record_1:content_sha256_is_invalid", violations)
        self.assertIn("record_2:source_is_missing_from_manifest", violations)

    def test_empty_records_and_invalid_manifest_fail(self):
        self.assertEqual(("at_least_one_retrieval_record_is_required",), retrieval_evidence_integrity_violations([], expected_hashes={"doc-1": DIGEST}))
        with self.assertRaises(ValueError):
            retrieval_evidence_integrity_violations([], expected_hashes={"doc-1": "BAD"})


if __name__ == "__main__":
    unittest.main()
