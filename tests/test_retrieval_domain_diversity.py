import unittest

from scripts.retrieval_domain_diversity import distinct_source_domains, retrieval_has_domain_diversity


class RetrievalDomainDiversityTests(unittest.TestCase):
    def test_distinct_domains_pass(self):
        results = [{"source_url": "https://docs.example/a"}, {"source_url": "https://standards.example/b"}]
        self.assertTrue(retrieval_has_domain_diversity(results))

    def test_duplicate_and_case_variant_domains_are_collapsed(self):
        results = [{"source_url": "https://Docs.Example/a"}, {"source_url": "https://docs.example/b"}]
        self.assertEqual(("docs.example",), distinct_source_domains(results))
        self.assertFalse(retrieval_has_domain_diversity(results))

    def test_invalid_minimum_is_rejected(self):
        with self.assertRaises(ValueError):
            retrieval_has_domain_diversity([], minimum_domains=0)


if __name__ == "__main__":
    unittest.main()
