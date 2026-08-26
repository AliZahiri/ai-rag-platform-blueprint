import unittest

from scripts.retrieval_query_expansion_budget import (
    query_expansion_budget_violations,
    query_expansion_is_within_budget,
)


class RetrievalQueryExpansionBudgetTests(unittest.TestCase):
    def test_bounded_unique_expansion_preserving_original_passes(self):
        queries = ["blue green deployment", "compose traffic promotion", "nginx upstream switch"]

        self.assertTrue(query_expansion_is_within_budget("blue green deployment", queries))

    def test_excess_duplicate_and_missing_original_queries_fail(self):
        violations = query_expansion_budget_violations(
            "source query",
            ["first", "FIRST", "", "query that is too long"],
            max_expansions=3,
            max_query_chars=10,
        )

        self.assertIn("expanded_query_count_exceeds_budget", violations)
        self.assertIn("expanded_query_1:query_must_be_unique", violations)
        self.assertIn("expanded_query_2:query_is_required", violations)
        self.assertIn("expanded_query_3:query_exceeds_character_budget", violations)
        self.assertIn("original_query_must_be_preserved", violations)

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            query_expansion_budget_violations("query", ["query"], max_expansions=0)


if __name__ == "__main__":
    unittest.main()
