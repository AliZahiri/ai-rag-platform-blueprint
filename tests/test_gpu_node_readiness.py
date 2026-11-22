import json
import subprocess
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.gpu_node_readiness import gpu_node_readiness_violations


NOW = datetime(2026, 11, 22, 12, tzinfo=timezone.utc)
MODEL_DIGEST = "sha256:" + "a" * 64
ROLLBACK_DIGEST = "sha256:" + "b" * 64


def ready_observation() -> dict[str, object]:
    return {
        "node": "gpu-01",
        "driver_version": "550.90.07",
        "container_runtime": "nvidia-container-toolkit",
        "gpu_count": 2,
        "model_cache_ready": True,
        "health_check_passed": True,
        "gpu_metrics_available": True,
        "rollback_ready": True,
        "model_image_digest": MODEL_DIGEST,
        "rollback_image_digest": ROLLBACK_DIGEST,
        "observed_at": "2026-11-22T11:55:00Z",
    }


class GpuNodeReadinessGateTests(unittest.TestCase):
    def test_fresh_complete_node_passes(self):
        self.assertEqual((), gpu_node_readiness_violations([ready_observation()], now=NOW))

    def test_duplicate_incomplete_stale_and_non_immutable_nodes_fail(self):
        invalid = ready_observation()
        invalid.update(
            {
                "driver_version": "",
                "gpu_count": 0,
                "health_check_passed": False,
                "rollback_ready": False,
                "model_image_digest": "latest",
                "rollback_image_digest": MODEL_DIGEST,
                "observed_at": "2026-11-20T12:00:00Z",
            }
        )
        same_digest = ready_observation()
        same_digest["node"] = "gpu-02"
        same_digest["rollback_image_digest"] = MODEL_DIGEST
        violations = gpu_node_readiness_violations([invalid, invalid, same_digest], now=NOW)

        self.assertIn("node_1:node_must_be_unique", violations)
        self.assertIn("node_0:driver_version_is_required", violations)
        self.assertIn("node_0:gpu_count_is_below_minimum", violations)
        self.assertIn("node_0:health_check_passed_must_be_true", violations)
        self.assertIn("node_0:rollback_ready_must_be_true", violations)
        self.assertIn("node_0:model_image_digest_must_be_immutable", violations)
        self.assertIn("node_2:rollback_image_digest_must_differ", violations)
        self.assertIn("node_0:readiness_evidence_is_not_fresh", violations)

    def test_invalid_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            gpu_node_readiness_violations([], now=NOW, maximum_age_seconds=0)
        with self.assertRaises(ValueError):
            gpu_node_readiness_violations([], now=NOW, minimum_gpu_count=0)

    def test_cli_emits_a_passing_machine_readable_report(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "python3",
                "scripts/gpu_node_readiness.py",
                "examples/gpu-node-readiness.example.json",
                "--now",
                "2026-11-22T12:00:00Z",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            {
                "maximum_age_seconds": 900,
                "minimum_gpu_count": 1,
                "status": "pass",
                "violations": [],
            },
            json.loads(result.stdout),
        )

    def test_cli_rejects_invalid_policy_timestamp(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "python3",
                "scripts/gpu_node_readiness.py",
                "examples/gpu-node-readiness.example.json",
                "--now",
                "not-a-timestamp",
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("error", json.loads(result.stderr)["status"])


if __name__ == "__main__":
    unittest.main()
