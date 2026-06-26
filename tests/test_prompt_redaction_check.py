import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/prompt_redaction_check.py"
SPEC = importlib.util.spec_from_file_location("prompt_redaction_check", SCRIPT_PATH)
prompt_redaction_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prompt_redaction_check)


class PromptRedactionCheckTests(unittest.TestCase):
    def test_sensitive_fields_are_detected(self):
        fields = prompt_redaction_check.detected_sensitive_fields(
            "email me at user@example.com or 09121234567 and card 6219-8610-1234-5678"
        )

        self.assertIn("email", fields)
        self.assertIn("phone", fields)
        self.assertIn("bank_card", fields)

    def test_safe_prompt_does_not_require_redaction(self):
        self.assertFalse(prompt_redaction_check.prompt_requires_redaction("Summarize this public policy."))

    def test_redact_prompt_masks_detected_values(self):
        redacted = prompt_redaction_check.redact_prompt(
            "Contact user@example.com with IBAN IR123456789012345678901234"
        )

        self.assertNotIn("user@example.com", redacted)
        self.assertNotIn("IR123456789012345678901234", redacted)
        self.assertIn("[REDACTED]", redacted)


if __name__ == "__main__":
    unittest.main()
