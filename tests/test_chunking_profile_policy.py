import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/chunking_profile_policy.py"
SPEC = importlib.util.spec_from_file_location("chunking_profile_policy", SCRIPT_PATH)
chunking_profile_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chunking_profile_policy)


class ChunkingProfilePolicyTests(unittest.TestCase):
    def test_valid_profile_passes(self):
        profile = {"chunk_size": 1200, "overlap": 120, "parser_profile": "pdf-default", "embedding_model": "text-embedding"}

        self.assertTrue(chunking_profile_policy.chunking_profile_is_safe(profile))

    def test_invalid_overlap_is_reported(self):
        warnings = chunking_profile_policy.chunking_profile_warnings({"chunk_size": 500, "overlap": 500})

        self.assertIn("overlap_must_be_smaller_than_chunk_size", warnings)
        self.assertIn("parser_profile_missing", warnings)


if __name__ == "__main__":
    unittest.main()
