import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/prompt_redaction_check.py"
SPEC = importlib.util.spec_from_file_location("prompt_redaction_check", SCRIPT_PATH)
prompt_redaction_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prompt_redaction_check)


class PromptRedactionCheckTests(unittest.TestCase):
    def test_sensitive_fields_are_detected(self):
        fields = prompt_redaction_check.detected_sensitive_fields("email me at user@example.com or 09121234567")

        self.assertIn("email", fields)
        self.assertIn("phone", fields)

    def test_safe_prompt_does_not_require_redaction(self):
        self.assertFalse(prompt_redaction_check.prompt_requires_redaction("Summarize this public policy."))


if __name__ == "__main__":
    unittest.main()
