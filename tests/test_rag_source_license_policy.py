import unittest

from scripts.rag_source_license_policy import source_license_violations, sources_have_allowed_licenses


class RagSourceLicenseAllowlistGateTests(unittest.TestCase):
    def test_allowlisted_unique_sources_pass(self):
        sources = [{"source_id": "handbook", "license": "CC-BY-4.0"}, {"source_id": "runbook", "license": "Apache-2.0"}]
        self.assertTrue(sources_have_allowed_licenses(sources, {"cc-by-4.0", "apache-2.0"}))

    def test_missing_duplicate_and_unapproved_licenses_fail(self):
        violations = source_license_violations([{"source_id": "handbook", "license": "Proprietary"}, {"source_id": "handbook"}], {"CC-BY-4.0"})
        self.assertEqual(violations, ("source_0:license_is_not_allowed", "source_1:source_id_must_be_unique", "source_1:license_is_not_allowed"))


if __name__ == "__main__":
    unittest.main()
