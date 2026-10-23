import importlib.util
import io
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts/collect_platform_readiness.py"
SPEC = importlib.util.spec_from_file_location("collect_platform_readiness", SCRIPT_PATH)
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


class _Response:
    def __init__(self, status: int):
        self.status = status
        self.closed = False

    def close(self):
        self.closed = True


class PlatformReadinessCollectorTests(unittest.TestCase):
    def setUp(self):
        self.now = lambda: datetime(2026, 10, 23, 8, 0, tzinfo=timezone.utc)

    def test_healthy_endpoint_records_bounded_metadata(self):
        response = _Response(204)
        result = collector.collect_endpoint_readiness(
            "vector-db",
            "https://vector.example/healthz",
            opener=lambda request, timeout: response,
            now=self.now,
            monotonic=iter((1.0, 1.025)).__next__,
        )

        self.assertEqual("healthy", result["status"])
        self.assertEqual(204, result["status_code"])
        self.assertEqual(25.0, result["latency_ms"])
        self.assertEqual("2026-10-23T08:00:00Z", result["checked_at"])
        self.assertTrue(response.closed)

    def test_credential_bearing_endpoint_is_not_requested(self):
        def fail_if_called(*args, **kwargs):
            raise AssertionError("invalid endpoint must not be requested")

        result = collector.collect_endpoint_readiness(
            "vector-db",
            "https://token@vector.example/healthz?api_key=secret",
            opener=fail_if_called,
            now=self.now,
        )

        self.assertEqual("invalid", result["status"])
        self.assertIn("endpoint_must_not_contain_credentials_or_parameters", result["violations"])
        self.assertNotIn("endpoint", result)

    def test_unavailable_service_does_not_expose_network_error_text(self):
        result = collector.collect_endpoint_readiness(
            "grafana",
            "https://grafana.example/api/health",
            opener=lambda request, timeout: (
                _ for _ in ()
            ).throw(URLError("internal host details")),
            now=self.now,
            monotonic=iter((1.0, 1.01)).__next__,
        )

        self.assertEqual("unavailable", result["status"])
        self.assertEqual("URLError", result["error_type"])
        self.assertNotIn("internal host details", str(result))

    def test_required_unhealthy_service_degrades_platform_report(self):
        report = collector.collect_platform_readiness(
            [
                ("vector-db", "https://vector.example/healthz", True),
                ("litellm", "https://router.example/health", False),
            ],
            opener=lambda request, timeout: _Response(
                503 if "vector" in request.full_url else 200
            ),
            now=self.now,
            monotonic=iter((1.0, 1.01, 2.0, 2.01)).__next__,
        )

        self.assertEqual("degraded", report["status"])
        self.assertEqual(["vector-db"], report["failed_required_services"])
        self.assertEqual(["vector-db"], report["required_services"])

    def test_endpoint_validation_rejects_non_http_or_query_input(self):
        self.assertIn("http_endpoint_is_required", collector.validate_endpoint("tcp://vector.example:6333"))
        self.assertIn(
            "endpoint_must_not_contain_credentials_or_parameters",
            collector.validate_endpoint("https://vector.example/healthz?token=secret"),
        )

    def test_timeout_is_bounded(self):
        with self.assertRaises(ValueError):
            collector.collect_endpoint_readiness(
                "vector-db", "https://vector.example/healthz", timeout_seconds=11
            )

    def test_cli_returns_input_error_for_invalid_endpoint_report(self):
        invalid_report = {
            "status": "degraded",
            "observations": [{"name": "vector-db", "status": "invalid"}],
        }
        with patch.object(collector, "collect_platform_readiness", return_value=invalid_report):
            with patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(
                    2,
                    collector.main(["--vector-db-url", "tcp://vector.example:6333"]),
                )


if __name__ == "__main__":
    unittest.main()
