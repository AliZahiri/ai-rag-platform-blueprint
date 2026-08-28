import unittest

from scripts.llm_usage_reconciliation import usage_reconciles, usage_reconciliation_violations


class LlmUsageReconciliationTests(unittest.TestCase):
    def test_matching_gateway_and_provider_usage_passes(self):
        records = [{"request_id": "req-1", "input_tokens": 100, "output_tokens": 20, "cost_usd": 0.01}, {"request_id": "req-2", "input_tokens": 50, "output_tokens": 10, "cost_usd": 0.005}]
        provider = {"request_count": 2, "input_tokens": 150, "output_tokens": 30, "cost_usd": 0.015}
        self.assertTrue(usage_reconciles(records, provider))

    def test_duplicate_request_and_provider_drift_fail(self):
        records = [{"request_id": "req-1", "input_tokens": 100, "output_tokens": 20, "cost_usd": 0.01}, {"request_id": "req-1", "input_tokens": 50, "output_tokens": 10, "cost_usd": 0.005}]
        provider = {"request_count": 1, "input_tokens": 120, "output_tokens": 10, "cost_usd": 0.05}
        violations = usage_reconciliation_violations(records, provider)
        self.assertIn("record_1:request_id_must_be_unique", violations)
        self.assertIn("provider_input_tokens_does_not_reconcile", violations)
        self.assertIn("provider_cost_usd_does_not_reconcile", violations)

    def test_invalid_measurements_and_policy_fail(self):
        violations = usage_reconciliation_violations([{"request_id": "req-1", "input_tokens": True, "output_tokens": -1, "cost_usd": float("inf")}], {"request_count": 1, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
        self.assertIn("record_0:input_tokens_must_be_non_negative", violations)
        self.assertIn("record_0:cost_usd_must_be_finite_and_non_negative", violations)
        with self.assertRaises(ValueError):
            usage_reconciliation_violations([], {}, maximum_token_delta=-1)
