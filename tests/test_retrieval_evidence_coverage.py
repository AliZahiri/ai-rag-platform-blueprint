import unittest

from scripts.retrieval_evidence_coverage import evidence_coverage_is_complete, uncovered_claim_ids


class RetrievalEvidenceCoverageTests(unittest.TestCase):
    def test_all_claims_with_evidence_pass(self):
        self.assertTrue(evidence_coverage_is_complete(["claim-1"], {"claim-1": ["source-7"]}))

    def test_claim_without_evidence_is_reported(self):
        self.assertEqual(("claim-2",), uncovered_claim_ids(["claim-1", "claim-2"], {"claim-1": ["source-7"]}))


if __name__ == "__main__":
    unittest.main()
