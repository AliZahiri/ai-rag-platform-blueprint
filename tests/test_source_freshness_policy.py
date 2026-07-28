import importlib.util
import unittest
from datetime import date
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/source_freshness_policy.py"
SPEC = importlib.util.spec_from_file_location("source_freshness_policy", SCRIPT_PATH)
source_freshness_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source_freshness_policy)


class SourceFreshnessPolicyTests(unittest.TestCase):
    def test_recent_valid_source_passes(self):
        source = {"status": "valid", "last_reviewed_at": date(2026, 7, 1)}

        self.assertTrue(source_freshness_policy.source_is_fresh(source, today=date(2026, 7, 5)))

    def test_stale_source_is_reported(self):
        warnings = source_freshness_policy.source_freshness_warnings({"status": "valid", "last_reviewed_at": date(2025, 1, 1)}, today=date(2026, 7, 5))

        self.assertIn("source_review_is_stale", warnings)

    def test_future_review_date_is_rejected(self):
        warnings = source_freshness_policy.source_freshness_warnings(
            {"status": "valid", "last_reviewed_at": date(2026, 8, 1)},
            today=date(2026, 7, 5),
        )

        self.assertEqual(("source_review_is_in_future",), warnings)

    def test_age_budget_must_be_a_positive_integer(self):
        with self.assertRaises(ValueError):
            source_freshness_policy.source_freshness_warnings(
                {"status": "valid", "last_reviewed_at": date(2026, 7, 1)},
                today=date(2026, 7, 5),
                max_age_days=True,
            )


if __name__ == "__main__":
    unittest.main()
