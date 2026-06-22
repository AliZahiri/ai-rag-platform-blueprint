import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/chat_retention_policy.py"
SPEC = importlib.util.spec_from_file_location("chat_retention_policy", SCRIPT_PATH)
chat_retention_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chat_retention_policy)


class ChatRetentionPolicyTests(unittest.TestCase):
    def test_complete_policy_is_reviewable(self):
        policy = {field: "set" for field in chat_retention_policy.REQUIRED_RETENTION_FIELDS}

        self.assertTrue(chat_retention_policy.retention_policy_is_reviewable(policy))

    def test_missing_policy_fields_are_reported(self):
        missing = chat_retention_policy.missing_retention_fields({"user_history_days": 30})

        self.assertIn("operational_log_days", missing)
        self.assertIn("support_access_scope", missing)


if __name__ == "__main__":
    unittest.main()
