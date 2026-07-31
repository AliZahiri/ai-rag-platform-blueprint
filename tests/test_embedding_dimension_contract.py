import unittest

from scripts.embedding_dimension_contract import embedding_bindings_are_compatible, embedding_dimension_violations


class EmbeddingDimensionContractTests(unittest.TestCase):
    def test_unique_complete_compatible_bindings_pass(self):
        bindings = [{"route": "documents", "provider": "local", "model": "embed-v2", "index": "documents-v2", "output_dimension": 768, "index_dimension": 768}]
        self.assertTrue(embedding_bindings_are_compatible(bindings))

    def test_dimension_mismatch_and_duplicate_route_are_reported(self):
        bindings = [{"route": "documents", "provider": "local", "model": "embed-v2", "index": "documents-v2", "output_dimension": 768, "index_dimension": 1536}, {"route": "documents", "provider": "local", "model": "embed-v3", "index": "documents-v3", "output_dimension": 1536, "index_dimension": 1536}]
        violations = embedding_dimension_violations(bindings)
        self.assertIn("binding_0:embedding_and_index_dimensions_must_match", violations)
        self.assertIn("binding_1:route_must_be_unique", violations)

    def test_empty_and_invalid_metadata_fail(self):
        self.assertEqual(("at_least_one_embedding_binding_is_required",), embedding_dimension_violations([]))
        violations = embedding_dimension_violations([{"route": "", "provider": "", "model": "", "index": "", "output_dimension": True, "index_dimension": 0}])
        self.assertEqual(6, len(violations))


if __name__ == "__main__":
    unittest.main()
