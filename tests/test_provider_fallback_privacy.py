import unittest

from scripts.provider_fallback_privacy import provider_fallback_privacy_is_safe, provider_fallback_privacy_violations


class ProviderFallbackPrivacyContractTests(unittest.TestCase):
    def test_primary_and_fallback_with_equivalent_privacy_pass(self):
        routes = [{"route_id": "chat", "providers": [{"provider_id": "primary", "region": "eu-central", "retention_days": 0, "training_use_permitted": False}, {"provider_id": "fallback", "region": "eu-west", "retention_days": 7, "training_use_permitted": False}]}]
        self.assertTrue(provider_fallback_privacy_is_safe(routes, allowed_regions=("eu-central", "eu-west")))

    def test_fallback_privacy_downgrade_fails(self):
        routes = [{"route_id": "chat", "providers": [{"provider_id": "primary", "region": "eu-central", "retention_days": 0, "training_use_permitted": False}, {"provider_id": "fallback", "region": "us-east", "retention_days": 90, "training_use_permitted": True}]}]
        violations = provider_fallback_privacy_violations(routes, allowed_regions=("eu-central",))
        self.assertIn("route_0:provider_1:region_is_not_approved", violations)
        self.assertIn("route_0:provider_1:retention_exceeds_policy", violations)
        self.assertIn("route_0:provider_1:training_use_must_be_disabled", violations)

    def test_missing_fallback_and_invalid_policy_fail(self):
        routes = [{"route_id": "chat", "providers": []}]
        self.assertIn("route_0:primary_and_fallback_providers_are_required", provider_fallback_privacy_violations(routes, allowed_regions=("eu",)))
        with self.assertRaises(ValueError):
            provider_fallback_privacy_violations(routes, allowed_regions=())
