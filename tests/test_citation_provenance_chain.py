import unittest

from scripts.citation_provenance_chain import citation_provenance_is_complete, citation_provenance_violations


class CitationProvenanceChainGateTests(unittest.TestCase):
    def test_complete_chain_for_answer_snapshot_passes(self):
        citations = [{"source_id": "policy-1", "content_sha256": "a" * 64, "captured_at": "2026-08-10T06:00:00Z", "index_snapshot": "index-42"}]

        self.assertTrue(citation_provenance_is_complete(citations, index_snapshot="index-42"))

    def test_invalid_duplicate_and_cross_snapshot_evidence_fails(self):
        citations = [{"source_id": "policy-1", "content_sha256": "invalid", "captured_at": "2026-08-10T06:00:00", "index_snapshot": "old"}, {"source_id": "policy-1", "content_sha256": "b" * 64, "captured_at": "2026-08-10T06:00:00Z", "index_snapshot": "index-42"}]

        violations = citation_provenance_violations(citations, index_snapshot="index-42")

        self.assertIn("citation_0:content_sha256_is_invalid", violations)
        self.assertIn("citation_0:captured_at_must_be_timezone_aware", violations)
        self.assertIn("citation_0:index_snapshot_must_match_answer", violations)
        self.assertIn("citation_1:source_id_must_be_unique", violations)

    def test_empty_citations_and_invalid_snapshot_fail(self):
        self.assertEqual(("at_least_one_citation_is_required",), citation_provenance_violations([], index_snapshot="index-42"))
        with self.assertRaises(ValueError):
            citation_provenance_violations([], index_snapshot="")


if __name__ == "__main__":
    unittest.main()
