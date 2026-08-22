import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GATE = REPOSITORY_ROOT / "scripts" / "chat_retention_policy_gate.py"


class ChatRetentionPolicyGateTests(unittest.TestCase):
    def run_gate(self, contents: str) -> subprocess.CompletedProcess[str]:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as policy_file:
            policy_file.write(contents)
            policy_file.flush()
            return subprocess.run(
                [sys.executable, str(GATE), policy_file.name],
                cwd=REPOSITORY_ROOT / "scripts",
                text=True,
                capture_output=True,
                check=False,
            )

    def test_valid_policy_emits_a_passing_structured_report(self):
        result = self.run_gate(
            json.dumps(
                {
                    "user_history_days": 90,
                    "operational_log_days": 30,
                    "anonymization_required": True,
                    "backup_retention_days": 14,
                    "support_access_scope": "case-by-case approval",
                }
            )
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {"missing_fields": [], "ok": True, "warnings": []},
        )

    def test_unsafe_policy_fails_with_machine_readable_warnings(self):
        result = self.run_gate(json.dumps({"user_history_days": 0}))

        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertIn("operational_log_days", report["missing_fields"])
        self.assertIn("user_history_days_must_be_positive_days", report["warnings"])

    def test_malformed_json_fails_without_a_traceback(self):
        result = self.run_gate("{")

        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertTrue(report["warnings"][0].startswith("unable_to_load_policy:"))
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
