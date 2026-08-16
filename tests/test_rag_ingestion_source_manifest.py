import unittest

from scripts.rag_ingestion_source_manifest import source_manifest_is_traceable, source_manifest_violations


class RagIngestionSourceManifestContractTests(unittest.TestCase):
    def test_traceable_manifest_passes(self):
        self.assertTrue(source_manifest_is_traceable({"source_id": "handbook-42", "content_sha256": "a" * 64, "retrieved_at": "2026-08-16T12:00:00Z", "license": "CC-BY-4.0"}))

    def test_incomplete_manifest_reports_each_violation(self):
        violations = source_manifest_violations({"source_id": " ", "content_sha256": "bad", "retrieved_at": "2026-08-16T12:00:00"})
        self.assertEqual(violations, ("source_id_is_required", "content_sha256_is_invalid", "retrieved_at_must_be_timezone_aware", "license_is_required"))


if __name__ == "__main__":
    unittest.main()
