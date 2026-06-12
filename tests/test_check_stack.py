import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CheckStackTests(unittest.TestCase):
    def test_plan_lists_observable_endpoints(self):
        result = subprocess.run(
            ["bash", "scripts/check-stack.sh", "--plan"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )

        self.assertIn("vector-db", result.stdout)
        self.assertIn("prometheus", result.stdout)
        self.assertIn("grafana", result.stdout)


if __name__ == "__main__":
    unittest.main()
