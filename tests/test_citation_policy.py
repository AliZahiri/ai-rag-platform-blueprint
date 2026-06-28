import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/citation_policy.py"
SPEC = importlib.util.spec_from_file_location("citation_policy", SCRIPT_PATH)
citation_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(citation_policy)


class CitationPolicyTests(unittest.TestCase):
    def test_source_backed_answer_requires_citation(self):
        warnings = citation_policy.citation_policy_warnings({"mode": "source_backed", "citation_count": 0})

        self.assertIn("source_backed_answer_needs_citations", warnings)

    def test_general_guidance_can_pass_without_citations(self):
        self.assertTrue(citation_policy.citation_policy_is_satisfied({"mode": "general_guidance"}))


if __name__ == "__main__":
    unittest.main()
