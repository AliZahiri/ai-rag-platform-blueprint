import unittest
from datetime import datetime, timezone
from hashlib import sha256

from scripts.response_pii_redaction import response_is_safe_to_release, response_pii_redaction_violations


NOW = datetime(2026, 8, 13, 6, 0, tzinfo=timezone.utc)


def report_for(response: str) -> dict[str, object]:
    return {"response_sha256": sha256(response.encode("utf-8")).hexdigest(), "detector_version": "pii-rules-v1", "scanned_at": "2026-08-13T05:55:00Z", "detected_categories": [], "release_decision": "allowed"}


class ResponsePiiRedactionEvidenceGateTests(unittest.TestCase):
    def test_fresh_clean_response_with_matching_evidence_passes(self):
        response = "The deployment completed and the readiness check passed."
        self.assertTrue(response_is_safe_to_release(response, report_for(response), now=NOW))

    def test_sensitive_response_with_tampered_stale_evidence_fails(self):
        response = "Contact user@example.com before enabling the route."
        report = report_for(response)
        report.update({"response_sha256": "bad", "scanned_at": "2026-08-13T04:00:00Z", "detected_categories": [], "release_decision": "allowed"})
        violations = response_pii_redaction_violations(response, report, now=NOW)
        self.assertIn("response_digest_must_match_content", violations)
        self.assertIn("scan_is_stale", violations)
        self.assertIn("detected_categories_must_match_response", violations)
        self.assertIn("response_contains_sensitive_data", violations)
        self.assertIn("sensitive_response_must_be_blocked", violations)

    def test_invalid_policy_and_naive_clock_fail(self):
        with self.assertRaises(ValueError):
            response_pii_redaction_violations("safe", {}, now=NOW, maximum_age_seconds=0)
        with self.assertRaises(ValueError):
            response_pii_redaction_violations("safe", {}, now=datetime(2026, 8, 13, 6, 0))


if __name__ == "__main__":
    unittest.main()
