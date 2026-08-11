import unittest

from scripts.prompt_template_contract import prompt_template_contract_is_safe, prompt_template_contract_violations


class PromptTemplateVersionContractTests(unittest.TestCase):
    def test_reviewed_immutable_template_passes(self):
        template = {"template_id": "support-answer", "version": "1.2.0", "content_sha256": "a" * 64, "approved": True, "reviewed_at": "2026-08-11T08:00:00Z"}
        self.assertTrue(prompt_template_contract_is_safe(template))

    def test_unreviewed_mutable_and_invalid_metadata_fails(self):
        violations = prompt_template_contract_violations({"template_id": "Support Answer", "version": "latest", "content_sha256": "bad", "approved": False, "reviewed_at": "2026-08-11T08:00:00"})
        self.assertIn("template_id_must_be_a_stable_slug", violations)
        self.assertIn("version_must_be_semver", violations)
        self.assertIn("content_sha256_is_invalid", violations)
        self.assertIn("template_must_be_explicitly_approved", violations)
        self.assertIn("reviewed_at_must_be_timezone_aware", violations)


if __name__ == "__main__":
    unittest.main()
