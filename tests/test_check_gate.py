import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github/scripts/check_gate.py"
SPEC = importlib.util.spec_from_file_location("check_gate", SCRIPT_PATH)
check_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_gate)


def check_run(name, *, status="COMPLETED", conclusion="SUCCESS"):
    return {
        "name": name,
        "status": status,
        "conclusion": conclusion,
    }


class CheckGateTests(unittest.TestCase):
    def test_all_required_pr_checks_must_succeed(self):
        payload = {"statusCheckRollup": [check_run("python"), check_run("Ansible syntax")]}

        self.assertEqual(
            ("ready", ()),
            check_gate.evaluate_check_runs(
                payload,
                required_names=("python", "Ansible syntax"),
            ),
        )

    def test_pending_and_missing_checks_block_merge(self):
        payload = {"statusCheckRollup": [check_run("python", status="IN_PROGRESS", conclusion=None)]}

        self.assertEqual(
            ("pending", ("missing:Ansible syntax", "pending:python")),
            check_gate.evaluate_check_runs(
                payload,
                required_names=("python", "Ansible syntax"),
            ),
        )

    def test_failed_check_blocks_merge(self):
        payload = {"statusCheckRollup": [check_run("python", conclusion="FAILURE")]}

        self.assertEqual(
            ("failed", ("python",)),
            check_gate.evaluate_check_runs(
                payload,
                required_names=("python",),
            ),
        )

    def test_empty_pr_rollup_cannot_satisfy_gate(self):
        payload = {"statusCheckRollup": []}

        self.assertEqual(
            ("pending", ("missing:python",)),
            check_gate.evaluate_check_runs(
                payload,
                required_names=("python",),
            ),
        )


if __name__ == "__main__":
    unittest.main()
