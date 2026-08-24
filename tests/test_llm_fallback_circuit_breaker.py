import unittest

from scripts.llm_fallback_circuit_breaker import circuit_breaker_is_safe, circuit_breaker_violations


class LlmFallbackCircuitBreakerGateTests(unittest.TestCase):
    def test_open_breaker_with_retry_and_fallback_passes(self):
        evidence = {"state": "open", "consecutive_failures": 5, "failure_threshold": 3, "retry_at": "2026-08-23T08:05:00Z", "fallback_route": "secondary", "observed_at": "2026-08-23T08:00:00Z"}
        self.assertTrue(circuit_breaker_is_safe(evidence))

    def test_inconsistent_open_state_fails(self):
        violations = circuit_breaker_violations({"state": "open", "consecutive_failures": 1, "failure_threshold": 3, "retry_at": "naive", "fallback_route": "", "observed_at": "2026-08-23T08:00:00"})
        self.assertEqual(violations, ("open_state_requires_threshold_failures", "open_state_requires_timezone_aware_retry_at", "fallback_route_is_required", "observed_at_must_be_timezone_aware"))
