import unittest

from scripts.citation_source_ids import citation_source_warnings, citations_are_traceable


class CitationSourceIdTests(unittest.TestCase):
    def test_unique_located_sources_are_traceable(self):
        self.assertTrue(citations_are_traceable([{"source_id": "law-1", "location": "article-1"}]))

    def test_duplicate_sources_are_reported(self):
        warnings = citation_source_warnings([{"source_id": "law-1", "location": "a"}, {"source_id": "law-1", "location": "b"}])

        self.assertIn("citation_source_ids_must_be_unique", warnings)


if __name__ == "__main__":
    unittest.main()
