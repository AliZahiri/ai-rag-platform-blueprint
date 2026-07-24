import unittest

from scripts.provider_route_preflight import provider_route_preflight


class ProviderRoutePreflightTests(unittest.TestCase):
    def test_matching_provider_within_budget_is_eligible(self):
        provider = {"capabilities": {"json_mode": True}, "max_context_tokens": 16000}
        report = provider_route_preflight(provider, required_capabilities=("json_mode",), required_context_tokens=8000, prompt_tokens=1000, completion_tokens=500, max_total_tokens=2000)
        self.assertTrue(report["eligible"])
        self.assertEqual(1500, report["estimated_total_tokens"])

    def test_capability_and_budget_failures_are_combined(self):
        report = provider_route_preflight({"capabilities": {}, "max_context_tokens": 1000}, required_capabilities=("tools",), required_context_tokens=8000, prompt_tokens=1000, completion_tokens=1000, max_total_tokens=1500)
        self.assertFalse(report["eligible"] )
        self.assertGreaterEqual(len(report["violations"]), 3)


if __name__ == "__main__":
    unittest.main()
