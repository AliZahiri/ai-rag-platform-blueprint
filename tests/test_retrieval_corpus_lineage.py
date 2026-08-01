import unittest

from scripts.retrieval_corpus_lineage import retrieval_lineage_is_consistent, retrieval_lineage_violations


class RetrievalCorpusLineageTests(unittest.TestCase):
    def test_unique_records_from_expected_snapshot_and_index_pass(self):
        records = [{"source_id": "doc-1", "corpus_snapshot": "2026-08-01", "index_version": "idx-42"}]
        self.assertTrue(retrieval_lineage_is_consistent(records, expected_corpus_snapshot="2026-08-01", expected_index_version="idx-42"))

    def test_duplicate_source_and_mixed_lineage_are_reported(self):
        records = [{"source_id": "doc-1", "corpus_snapshot": "old", "index_version": "idx-42"}, {"source_id": "doc-1", "corpus_snapshot": "2026-08-01", "index_version": "idx-41"}]
        violations = retrieval_lineage_violations(records, expected_corpus_snapshot="2026-08-01", expected_index_version="idx-42")
        self.assertIn("record_0:corpus_snapshot_mismatch", violations)
        self.assertIn("record_1:source_id_must_be_unique", violations)
        self.assertIn("record_1:index_version_mismatch", violations)

    def test_empty_records_and_invalid_policy_fail(self):
        self.assertEqual(("at_least_one_retrieval_record_is_required",), retrieval_lineage_violations([], expected_corpus_snapshot="snapshot", expected_index_version="index"))
        with self.assertRaises(ValueError):
            retrieval_lineage_violations([], expected_corpus_snapshot="", expected_index_version="index")


if __name__ == "__main__":
    unittest.main()
