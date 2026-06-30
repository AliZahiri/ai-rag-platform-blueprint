import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/embedding_cache_policy.py"
SPEC = importlib.util.spec_from_file_location("embedding_cache_policy", SCRIPT_PATH)
embedding_cache_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(embedding_cache_policy)


class EmbeddingCachePolicyTests(unittest.TestCase):
    def test_complete_metadata_has_stable_key(self):
        metadata = {field: "value" for field in embedding_cache_policy.REQUIRED_CACHE_KEY_FIELDS}

        self.assertTrue(embedding_cache_policy.embedding_cache_key_is_stable(metadata))

    def test_missing_embedding_model_is_reported(self):
        missing = embedding_cache_policy.missing_cache_key_fields({"document_id": "1"})

        self.assertIn("embedding_model", missing)

    def test_cache_key_is_deterministic_and_normalized(self):
        key = embedding_cache_policy.build_embedding_cache_key(
            {
                "document_id": " Case-42 ",
                "content_checksum": "ABC123",
                "parser_profile": "PDF-Default",
                "embedding_model": "Text-Embedding-3",
            }
        )

        self.assertEqual(key, "case-42:abc123:pdf-default:text-embedding-3")


if __name__ == "__main__":
    unittest.main()
