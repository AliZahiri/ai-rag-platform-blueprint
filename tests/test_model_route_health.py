import unittest

from scripts.model_route_health import route_health_is_ready, route_health_warnings


class ModelRouteHealthTests(unittest.TestCase):
    def test_ready_route_passes_contract(self):
        route = {
            "alias": "rag-primary",
            "provider": "openai",
            "model": "gpt-example",
            "limits": {"timeout_seconds": 30, "max_retries": 1},
            "capabilities": {"streaming": True, "json_mode": True},
            "fallback": "rag-fallback",
        }

        self.assertTrue(route_health_is_ready(route, {"rag-primary", "rag-fallback"}))

    def test_missing_contract_items_are_reported(self):
        warnings = route_health_warnings({"alias": "rag-primary", "fallback": "missing"}, {"rag-primary"})

        self.assertIn("provider_is_required", warnings)
        self.assertIn("limits_must_be_object", warnings)
        self.assertIn("fallback_alias_is_unknown", warnings)


if __name__ == "__main__":
    unittest.main()
