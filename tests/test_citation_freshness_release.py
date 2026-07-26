import unittest
from datetime import date

from scripts.citation_freshness_release import citation_freshness_violations, citations_are_fresh_for_release


class CitationFreshnessReleaseTests(unittest.TestCase):
    def test_traceable_recent_sources_pass(self):
        sources = [{"source_id": "policy-1", "location": "s3://docs/policy.pdf", "status": "valid", "last_reviewed_at": date(2026, 7, 1)}]

        self.assertTrue(citations_are_fresh_for_release(sources, today=date(2026, 7, 25), max_age_days=90))

    def test_identity_and_freshness_failures_are_partitioned(self):
        sources = [{"source_id": "", "location": "", "status": "unknown", "last_reviewed_at": date(2025, 1, 1)}]

        violations = citation_freshness_violations(sources, today=date(2026, 7, 25), max_age_days=90)

        self.assertIn("citation_source_id_is_required", violations)
        self.assertIn("citation_source_location_is_required", violations)
        self.assertIn("source_0:source_status_unknown", violations)
        self.assertIn("source_0:source_review_is_stale", violations)

    def test_empty_sources_and_invalid_age_budget_fail(self):
        self.assertEqual(("at_least_one_citation_source_is_required",), citation_freshness_violations([], today=date(2026, 7, 25)))
        with self.assertRaises(ValueError):
            citation_freshness_violations([], today=date(2026, 7, 25), max_age_days=0)


if __name__ == "__main__":
    unittest.main()
