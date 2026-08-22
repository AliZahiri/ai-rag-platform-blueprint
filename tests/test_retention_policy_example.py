import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RetentionPolicyExampleTests(unittest.TestCase):
    def test_example_passes_the_cli_gate(self):
        result = subprocess.run([sys.executable, "scripts/chat_retention_policy_gate.py", "examples/retention-policy.example.json"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(json.loads(result.stdout)["ok"])
