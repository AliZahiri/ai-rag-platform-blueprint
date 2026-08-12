import unittest

from scripts.retrieval_source_license import retrieval_source_license_is_safe, retrieval_source_license_violations


class RetrievalSourceLicenseGateTests(unittest.TestCase):
    def test_permitted_owned_source_passes(self):
        sources = [{"source_id": "handbook", "license": "Proprietary-Internal", "ingestion_permitted": True, "owner": "knowledge-team"}]
        self.assertTrue(retrieval_source_license_is_safe(sources))

    def test_duplicate_unlicensed_and_unowned_source_fails(self):
        sources = [{"source_id": "handbook", "license": "Unknown", "ingestion_permitted": False, "owner": ""}, {"source_id": "handbook", "license": "MIT", "ingestion_permitted": True, "owner": "ops"}]
        violations = retrieval_source_license_violations(sources)
        self.assertIn("source_0:license_is_not_allowed", violations)
        self.assertIn("source_0:ingestion_permission_is_required", violations)
        self.assertIn("source_0:owner_is_required", violations)
        self.assertIn("source_1:source_id_must_be_unique", violations)


if __name__ == "__main__":
    unittest.main()
