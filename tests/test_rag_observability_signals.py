import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/rag_observability_signals.py"
SPEC = importlib.util.spec_from_file_location("rag_observability_signals", SCRIPT_PATH)
rag_observability_signals = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rag_observability_signals)


class RagObservabilitySignalsTests(unittest.TestCase):
    def test_complete_signal_set_passes(self):
        self.assertTrue(
            rag_observability_signals.rag_observability_is_complete(
                rag_observability_signals.REQUIRED_RAG_SIGNALS
            )
        )

    def test_missing_signals_are_reported(self):
        missing = rag_observability_signals.missing_rag_signals({"retrieval_latency_seconds"})

        self.assertIn("empty_retrieval_total", missing)
        self.assertIn("gpu_memory_utilization", missing)


if __name__ == "__main__":
    unittest.main()
