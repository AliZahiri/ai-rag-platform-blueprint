import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/chat_retention_policy.py"
SPEC = importlib.util.spec_from_file_location("chat_retention_policy", SCRIPT_PATH)
chat_retention_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chat_retention_policy)


class ChatRetentionPolicyTests(unittest.TestCase):
    def test_complete_policy_is_reviewable(self):
        policy = {
            "user_history_days": 90,
            "operational_log_days": 30,
            "anonymization_required": True,
            "backup_retention_days": 14,
            "support_access_scope": "case-by-case approval",
        }

        self.assertTrue(chat_retention_policy.retention_policy_is_reviewable(policy))

    def test_missing_policy_fields_are_reported(self):
        missing = chat_retention_policy.missing_retention_fields({"user_history_days": 30})

        self.assertIn("operational_log_days", missing)
        self.assertIn("support_access_scope", missing)

    def test_invalid_policy_values_block_review(self):
        policy = {
            "user_history_days": 0,
            "operational_log_days": "30",
            "anonymization_required": "yes",
            "backup_retention_days": 14,
            "support_access_scope": "",
        }

        warnings = chat_retention_policy.retention_policy_warnings(policy)

        self.assertIn("user_history_days_must_be_positive_days", warnings)
        self.assertIn("operational_log_days_must_be_positive_days", warnings)
        self.assertIn("anonymization_required_must_be_boolean", warnings)
        self.assertIn("support_access_scope_must_be_defined", warnings)
        self.assertFalse(chat_retention_policy.retention_policy_is_reviewable(policy))


if __name__ == "__main__":
    unittest.main()
