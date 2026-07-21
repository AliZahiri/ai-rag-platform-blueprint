import unittest

from scripts.provider_capability_match import provider_capability_violations, provider_matches_workload


class ProviderCapabilityMatchTests(unittest.TestCase):
    def test_matching_provider_passes(self):
        provider = {"capabilities": {"json_mode": True, "tools": True}, "max_context_tokens": 32768}
        self.assertTrue(provider_matches_workload(provider, required=("json_mode", "tools"), required_context_tokens=16000))

    def test_missing_capability_and_context_are_reported(self):
        provider = {"capabilities": {"json_mode": True}, "max_context_tokens": 4096}
        self.assertEqual(("capability_tools_is_required", "context_window_is_insufficient"), provider_capability_violations(provider, required=("json_mode", "tools"), required_context_tokens=8000))

    def test_non_positive_requirement_is_rejected(self):
        with self.assertRaises(ValueError):
            provider_capability_violations({}, required=(), required_context_tokens=0)


if __name__ == "__main__":
    unittest.main()
