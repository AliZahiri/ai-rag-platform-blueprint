import unittest

from scripts.llm_request_token_budget import llm_request_is_within_token_budget, llm_request_token_budget_violations


class LlmRequestTokenBudgetGateTests(unittest.TestCase):
    def test_request_within_route_capacity_passes(self):
        self.assertTrue(llm_request_is_within_token_budget({"input_tokens": 600, "reserved_output_tokens": 400}, {"context_window_tokens": 4096, "max_request_tokens": 2048}))

    def test_invalid_and_over_budget_request_fails(self):
        violations = llm_request_token_budget_violations({"input_tokens": 3500, "reserved_output_tokens": 1000}, {"context_window_tokens": 4096, "max_request_tokens": 3000})
        self.assertIn("request_exceeds_context_window", violations)
        self.assertIn("request_exceeds_route_budget", violations)
        self.assertIn("input_tokens_must_be_positive", llm_request_token_budget_violations({"input_tokens": 0, "reserved_output_tokens": 1}, {"context_window_tokens": 1, "max_request_tokens": 1}))


if __name__ == "__main__":
    unittest.main()
