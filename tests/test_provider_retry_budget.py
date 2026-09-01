import unittest

from scripts.provider_retry_budget import provider_retry_is_bounded, provider_retry_violations


class ProviderRetryBudgetTests(unittest.TestCase):
    def test_bounded_throttle_retry_passes(self):
        attempts = [{"request_id": "req-1", "attempt": 1, "provider": "primary", "status_code": 429, "delay_before_ms": 0}, {"request_id": "req-1", "attempt": 2, "provider": "fallback", "status_code": 200, "delay_before_ms": 500}]
        self.assertTrue(provider_retry_is_bounded(attempts))

    def test_non_retryable_status_and_delay_overrun_fail(self):
        attempts = [{"request_id": "req-1", "attempt": 1, "provider": "primary", "status_code": 400, "delay_before_ms": 0}, {"request_id": "req-1", "attempt": 2, "provider": "primary", "status_code": 200, "delay_before_ms": 6000}]
        violations = provider_retry_violations(attempts)
        self.assertIn("attempt_1:non_retryable_status_was_retried", violations)
        self.assertIn("cumulative_retry_delay_exceeds_budget", violations)

    def test_empty_attempts_and_invalid_policy_fail(self):
        self.assertEqual(("at_least_one_attempt_is_required",), provider_retry_violations([]))
        with self.assertRaises(ValueError):
            provider_retry_violations([], maximum_attempts=0)
