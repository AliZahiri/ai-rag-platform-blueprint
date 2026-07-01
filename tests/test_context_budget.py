import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/context_budget.py"
SPEC = importlib.util.spec_from_file_location("context_budget", SCRIPT_PATH)
context_budget = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context_budget)


class ContextBudgetTests(unittest.TestCase):
    def test_safe_budget_passes(self):
        plan = {"context_window_tokens": 16000, "prompt_tokens": 2000, "retrieved_chunk_tokens": 7000, "reserved_answer_tokens": 2000}

        self.assertTrue(context_budget.context_budget_is_safe(plan))

    def test_over_budget_plan_is_reported(self):
        plan = {"context_window_tokens": 8000, "prompt_tokens": 3000, "retrieved_chunk_tokens": 5000, "reserved_answer_tokens": 1000}

        self.assertIn("context_budget_exceeds_window", context_budget.context_budget_warnings(plan))


if __name__ == "__main__":
    unittest.main()
