import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/gpu_node_runbook.py"
SPEC = importlib.util.spec_from_file_location("gpu_node_runbook", SCRIPT_PATH)
gpu_node_runbook = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gpu_node_runbook)


class GpuNodeRunbookTests(unittest.TestCase):
    def test_complete_runbook_passes(self):
        self.assertTrue(gpu_node_runbook.gpu_runbook_is_complete(gpu_node_runbook.REQUIRED_GPU_RUNBOOK_SECTIONS))

    def test_missing_sections_are_reported(self):
        missing = gpu_node_runbook.missing_gpu_runbook_sections({"driver_prerequisites"})

        self.assertIn("model_cache", missing)
        self.assertIn("rollback_path", missing)


if __name__ == "__main__":
    unittest.main()
