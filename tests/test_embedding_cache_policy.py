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


if __name__ == "__main__":
    unittest.main()
