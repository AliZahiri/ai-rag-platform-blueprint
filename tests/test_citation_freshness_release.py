import unittest
from datetime import date
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.citation_freshness_release import (
    citation_freshness_report,
    citation_freshness_violations,
    citations_are_fresh_for_release,
)


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
        with self.assertRaises(ValueError):
            citation_freshness_violations([], today=date(2026, 7, 25), max_age_days=True)

    def test_report_exposes_release_decision_and_policy_inputs(self):
        report = citation_freshness_report(
            [{"source_id": "policy-1", "location": "s3://docs/policy.pdf", "status": "valid", "last_reviewed_at": date(2026, 7, 1)}],
            today=date(2026, 7, 25),
            max_age_days=90,
        )

        self.assertTrue(report["release_allowed"])
        self.assertEqual("2026-07-25", report["evaluated_on"])
        self.assertEqual(1, report["source_count"])

    def test_cli_parses_json_dates_and_returns_policy_exit_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "sources.json"
            input_path.write_text(
                json.dumps(
                    [
                        {
                            "source_id": "policy-1",
                            "location": "s3://docs/policy.pdf",
                            "status": "valid",
                            "last_reviewed_at": "2026-07-01",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "python3",
                    "scripts/citation_freshness_release.py",
                    str(input_path),
                    "--today",
                    "2026-07-25",
                    "--max-age-days",
                    "90",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(0, result.returncode)
        self.assertTrue(json.loads(result.stdout)["release_allowed"])

    def test_cli_rejects_non_array_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "sources.json"
            input_path.write_text("{}", encoding="utf-8")
            result = subprocess.run(
                ["python3", "scripts/citation_freshness_release.py", str(input_path), "--today", "2026-07-25"],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("must be a JSON array", result.stderr)


if __name__ == "__main__":
    unittest.main()
