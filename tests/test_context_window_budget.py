import unittest

from scripts.context_window_budget import context_budget_is_safe, context_budget_warnings


class ContextWindowBudgetTests(unittest.TestCase):
    def test_context_with_reserved_output_passes(self):
        self.assertTrue(context_budget_is_safe([400, 600], max_context_tokens=2000, reserved_output_tokens=500))

    def test_over_budget_context_is_reported(self):
        warnings = context_budget_warnings([900, 900], max_context_tokens=2000, reserved_output_tokens=300)

        self.assertIn("retrieved_context_exceeds_route_budget", warnings)


if __name__ == "__main__":
    unittest.main()
