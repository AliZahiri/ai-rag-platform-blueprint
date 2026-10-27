import importlib.util
import io
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/qdrant_restore_drill.py"
SPEC = importlib.util.spec_from_file_location("qdrant_restore_drill", SCRIPT_PATH)
drill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(drill)


class Response(io.BytesIO):
    status = 200

    def getcode(self):
        return self.status


def envelope(result):
    return json.dumps({"status": "ok", "result": result}).encode()


SOURCE_INFO = {"config": {"params": {"vectors": {"size": 3}}}}


class QdrantRestoreDrillTests(unittest.TestCase):
    def test_restore_drill_creates_gate_compatible_observation(self):
        requests = []

        def opener(request, timeout):
            requests.append(request)
            parsed = urlsplit(request.full_url)
            source = parsed.netloc == "source:6333"
            path = parsed.path
            method = request.get_method()
            if method == "GET" and path == "/collections/knowledge" and source:
                return Response(envelope(SOURCE_INFO))
            if method == "POST" and path == "/collections/knowledge/points/count":
                return Response(envelope({"count": 2 if source else 2}))
            if method == "POST" and path == "/collections/knowledge/points/scroll":
                return Response(envelope({"points": [{"id": 1, "vector": [0.1, 0.2, 0.3]}]}))
            if method == "GET" and path == "/collections/knowledge" and not source:
                if not any(item.get_method() == "POST" and item.full_url.endswith("/snapshots/upload?priority=snapshot&wait=true") for item in requests):
                    raise HTTPError(request.full_url, 404, "not found", {}, None)
                return Response(envelope(SOURCE_INFO))
            if method == "POST" and path == "/collections/knowledge/snapshots":
                return Response(envelope({"name": "knowledge.snapshot"}))
            if method == "GET" and path == "/collections/knowledge/snapshots/knowledge.snapshot":
                return Response(b"snapshot-bytes")
            if method == "POST" and path == "/collections/knowledge/snapshots/upload":
                return Response(envelope(True))
            if method == "POST" and path == "/collections/knowledge/points/search":
                return Response(envelope([{"id": 1, "score": 1.0}]))
            self.fail(f"unexpected request: {method} {request.full_url}")

        observation = drill.restore_observation(
            drill.QdrantClient("http://source:6333", opener=opener),
            drill.QdrantClient("http://target:6334", opener=opener),
            source_collection="knowledge",
            target_collection="knowledge",
            now=lambda: datetime(2026, 10, 24, 12, tzinfo=timezone.utc),
        )

        self.assertEqual(2, observation["expected_record_count"])
        self.assertEqual(3, observation["restored_dimension"])
        self.assertTrue(observation["sample_query_passed"])
        self.assertEqual(observation["expected_manifest_sha256"], observation["restored_manifest_sha256"])
        upload = next(item for item in requests if item.get_method() == "POST" and "/snapshots/upload" in item.full_url)
        self.assertIn(b"snapshot-bytes", upload.data)
        self.assertIn("multipart/form-data", upload.headers["Content-type"])

    def test_target_collection_must_be_empty_before_a_snapshot_is_created(self):
        calls = []

        def opener(request, timeout):
            calls.append(request)
            if request.get_method() == "GET" and "source:6333" in request.full_url:
                return Response(envelope(SOURCE_INFO))
            if request.get_method() == "POST" and request.full_url.endswith("/points/count"):
                return Response(envelope({"count": 1}))
            if request.get_method() == "POST" and request.full_url.endswith("/points/scroll"):
                return Response(envelope({"points": [{"id": 1, "vector": [0.1, 0.2, 0.3]}]}))
            if request.get_method() == "GET" and "target:6334" in request.full_url:
                return Response(envelope(SOURCE_INFO))
            self.fail(f"unexpected request: {request.get_method()} {request.full_url}")

        with self.assertRaisesRegex(drill.DrillError, "already exists"):
            drill.restore_observation(
                drill.QdrantClient("http://source:6333", opener=opener),
                drill.QdrantClient("http://target:6334", opener=opener),
                source_collection="knowledge",
                target_collection="knowledge",
            )

        self.assertFalse(any("/snapshots" in call.full_url for call in calls))

    def test_endpoint_and_collection_validation_reject_unsafe_input(self):
        with self.assertRaises(drill.DrillError):
            drill.normalize_endpoint("https://token@example.invalid")
        with self.assertRaises(drill.DrillError):
            drill.validate_collection_name("knowledge/production", label="collection")


if __name__ == "__main__":
    unittest.main()
