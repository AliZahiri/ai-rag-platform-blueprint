import unittest

from scripts.retrieval_source_deduplication import duplicate_source_ids, unique_source_ids


class RetrievalSourceDeduplicationTests(unittest.TestCase):
    def test_unique_source_ids_keep_first_seen_order(self):
        results = [{"source_id": "law-1"}, {"source_id": "law-2"}, {"source_id": "law-1"}]

        self.assertEqual(("law-1", "law-2"), unique_source_ids(results))

    def test_duplicate_source_ids_are_reported_once(self):
        self.assertEqual(("law-1",), duplicate_source_ids([{"source_id": "law-1"}, {"source_id": "law-1"}]))


if __name__ == "__main__":
    unittest.main()
