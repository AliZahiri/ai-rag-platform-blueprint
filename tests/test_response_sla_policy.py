import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/response_sla_policy.py"
SPEC = importlib.util.spec_from_file_location("response_sla_policy", SCRIPT_PATH)
response_sla_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(response_sla_policy)


class ResponseSlaPolicyTests(unittest.TestCase):
    def test_ready_sla_passes(self):
        policy = {"p95_latency_ms": 2500, "max_error_rate_pct": 1.0, "streaming_enabled": True, "owner": "platform"}

        self.assertTrue(response_sla_policy.response_sla_is_ready(policy))

    def test_invalid_sla_reports_warnings(self):
        warnings = response_sla_policy.response_sla_warnings({"p95_latency_ms": 0, "max_error_rate_pct": 120})

        self.assertIn("p95_latency_ms_must_be_positive", warnings)
        self.assertIn("owner_missing", warnings)


if __name__ == "__main__":
    unittest.main()
