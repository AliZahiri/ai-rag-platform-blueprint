import unittest

from scripts.claim_citation_coverage import claim_citation_coverage_violations


class ClaimCitationCoverageGateTests(unittest.TestCase):
    def test_all_support_required_claims_with_known_citations_pass(self):
        claims = [{"claim_id": "c1", "requires_support": True, "citation_ids": ["src-1"]}, {"claim_id": "c2", "requires_support": False, "citation_ids": []}]
        self.assertEqual((), claim_citation_coverage_violations(claims, known_citation_ids={"src-1"}))

    def test_missing_duplicate_and_unknown_citations_fail(self):
        claims = [{"claim_id": "c1", "requires_support": True, "citation_ids": []}, {"claim_id": "c1", "requires_support": True, "citation_ids": ["missing", "missing"]}]
        violations = claim_citation_coverage_violations(claims, known_citation_ids={"src-1"})
        self.assertIn("claim_1:claim_id_must_be_unique", violations)
        self.assertIn("claim_1:citation_ids_must_be_unique", violations)
        self.assertIn("claim_1:unknown_citation_reference", violations)
        self.assertIn("supported_claim_coverage_below_minimum", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            claim_citation_coverage_violations([], known_citation_ids=set())
        with self.assertRaises(ValueError):
            claim_citation_coverage_violations([], known_citation_ids={"src"}, minimum_coverage_ratio=1.1)


if __name__ == "__main__":
    unittest.main()
