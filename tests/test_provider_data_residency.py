import unittest
from datetime import datetime, timezone

from scripts.provider_data_residency import provider_data_residency_is_approved, provider_data_residency_violations


NOW = datetime(2026, 9, 3, 6, 0, tzinfo=timezone.utc)


class ProviderDataResidencyContractTests(unittest.TestCase):
    def test_recent_approved_no_training_contract_passes(self):
        providers = [{"provider_id": "managed-llm", "region": "eu-central", "retention_days": 0, "training_use_permitted": False, "contract_reviewed_at": "2026-08-03T06:00:00Z"}]
        self.assertTrue(provider_data_residency_is_approved(providers, allowed_regions=("eu-central",), now=NOW))

    def test_duplicate_unapproved_and_stale_contracts_fail(self):
        providers = [{"provider_id": "managed-llm", "region": "us-east", "retention_days": 90, "training_use_permitted": True, "contract_reviewed_at": "2025-01-01T00:00:00Z"}, {"provider_id": "managed-llm", "region": "eu-central", "retention_days": 0, "training_use_permitted": False, "contract_reviewed_at": "2026-08-03T06:00:00Z"}]
        violations = provider_data_residency_violations(providers, allowed_regions=("eu-central",), now=NOW)
        self.assertIn("provider_0:region_is_not_approved", violations)
        self.assertIn("provider_0:retention_days_exceed_policy", violations)
        self.assertIn("provider_0:training_use_must_be_disabled", violations)
        self.assertIn("provider_0:contract_review_is_stale_or_future_dated", violations)
        self.assertIn("provider_1:provider_id_must_be_unique", violations)

    def test_invalid_policy_fails(self):
        with self.assertRaises(ValueError):
            provider_data_residency_violations([], allowed_regions=(), now=NOW)
