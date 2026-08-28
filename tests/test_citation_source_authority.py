import unittest

from scripts.citation_source_authority import citation_source_authority_violations, critical_claims_have_authoritative_sources


class CitationSourceAuthorityEvidenceTests(unittest.TestCase):
    def test_reviewed_official_source_covers_critical_claim(self):
        citations = [{"source_id": "policy-1", "authority_tier": "official", "authority_reviewed": True, "claim_ids": ["claim-1"]}]
        self.assertTrue(critical_claims_have_authoritative_sources(citations, critical_claim_ids=["claim-1"]))

    def test_secondary_or_unreviewed_source_does_not_cover_critical_claim(self):
        citations = [{"source_id": "article-1", "authority_tier": "secondary", "authority_reviewed": True, "claim_ids": ["claim-1"]}, {"source_id": "policy-1", "authority_tier": "official", "authority_reviewed": False, "claim_ids": ["claim-2"]}]
        violations = citation_source_authority_violations(citations, critical_claim_ids=["claim-1", "claim-2"])
        self.assertIn("critical_claim_claim-1:verified_authoritative_source_is_required", violations)
        self.assertIn("critical_claim_claim-2:verified_authoritative_source_is_required", violations)

    def test_duplicate_sources_and_malformed_claim_metadata_fail(self):
        citations = [{"source_id": "source-1", "authority_tier": "primary", "authority_reviewed": True, "claim_ids": ["claim-1"]}, {"source_id": "source-1", "authority_tier": "unknown", "authority_reviewed": True, "claim_ids": []}]
        violations = citation_source_authority_violations(citations, critical_claim_ids=["claim-1", "claim-1"])
        self.assertIn("critical_claim_ids_must_be_unique", violations)
        self.assertIn("citation_1:source_id_must_be_unique", violations)
        self.assertIn("citation_1:authority_tier_is_invalid", violations)
