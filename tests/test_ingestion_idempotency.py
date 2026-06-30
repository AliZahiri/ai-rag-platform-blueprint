import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/ingestion_idempotency.py"
SPEC = importlib.util.spec_from_file_location("ingestion_idempotency", SCRIPT_PATH)
ingestion_idempotency = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ingestion_idempotency)


class IngestionIdempotencyTests(unittest.TestCase):
    def test_complete_metadata_is_idempotent(self):
        metadata = {field: "value" for field in ingestion_idempotency.REQUIRED_IDEMPOTENCY_FIELDS}

        self.assertTrue(ingestion_idempotency.ingestion_is_idempotent(metadata))

    def test_missing_fields_are_reported(self):
        missing = ingestion_idempotency.missing_idempotency_fields({"document_id": "doc-1"})

        self.assertIn("source_checksum", missing)
        self.assertIn("chunking_version", missing)


if __name__ == "__main__":
    unittest.main()
