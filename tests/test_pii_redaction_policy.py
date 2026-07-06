import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/pii_redaction_policy.py"
SPEC = importlib.util.spec_from_file_location("pii_redaction_policy", SCRIPT_PATH)
pii_redaction_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pii_redaction_policy)


class PiiRedactionPolicyTests(unittest.TestCase):
    def test_complete_coverage_passes(self):
        self.assertTrue(pii_redaction_policy.redaction_coverage_is_complete(set(pii_redaction_policy.REQUIRED_PII_CATEGORIES)))

    def test_missing_categories_are_reported(self):
        missing = pii_redaction_policy.missing_redaction_categories({"phone"})

        self.assertIn("national_id", missing)
        self.assertIn("case_tracking_number", missing)


if __name__ == "__main__":
    unittest.main()
