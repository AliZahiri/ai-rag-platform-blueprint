import unittest

from scripts.provider_latency_slo import provider_latency_slo_is_met, provider_latency_slo_violations


class ProviderLatencySloEvidenceTests(unittest.TestCase):
    def test_sufficient_ordered_distribution_passes(self):
        evidence = {"provider": "local-vllm", "sample_count": 500, "latency_ms": {"p50": 220, "p95": 900, "p99": 1400}, "error_rate": 0.002, "observed_at": "2026-08-29T08:00:00Z"}
        self.assertTrue(provider_latency_slo_is_met(evidence, maximum_p95_ms=1000))

    def test_undersampled_unordered_slow_and_erroring_provider_fails(self):
        evidence = {"provider": "", "sample_count": 10, "latency_ms": {"p50": 900, "p95": 2500, "p99": 2000}, "error_rate": 0.2, "observed_at": "2026-08-29T08:00:00"}
        violations = provider_latency_slo_violations(evidence)
        self.assertIn("sample_count_is_below_minimum", violations)
        self.assertIn("latency_percentiles_must_be_ordered", violations)
        self.assertIn("provider_p95_latency_exceeds_budget", violations)
        self.assertIn("provider_error_rate_exceeds_budget", violations)

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            provider_latency_slo_violations({}, minimum_samples=0)
