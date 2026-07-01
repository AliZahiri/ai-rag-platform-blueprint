import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/fallback_policy.py"
SPEC = importlib.util.spec_from_file_location("fallback_policy", SCRIPT_PATH)
fallback_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fallback_policy)


class FallbackPolicyTests(unittest.TestCase):
    def test_linear_fallback_chain_passes(self):
        self.assertTrue(fallback_policy.fallback_policy_is_valid({"fast": "safe", "safe": None}, primary="fast"))

    def test_cycle_and_missing_target_are_reported(self):
        warnings = fallback_policy.fallback_policy_warnings({"fast": "safe", "safe": "fast", "cheap": "missing"}, primary="fast")

        self.assertIn("fast_fallback_cycle_detected", warnings)
        self.assertIn("cheap_fallback_target_missing", warnings)


if __name__ == "__main__":
    unittest.main()
