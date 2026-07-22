import unittest

from scripts.provider_liveness_probe import probe_provider_liveness, validate_probe_endpoint


class _Response:
    status = 204


class ProviderLivenessProbeTests(unittest.TestCase):
    def test_disabled_probe_never_calls_opener(self):
        def fail_if_called(*args, **kwargs):
            raise AssertionError("network opener must not be called")

        self.assertEqual({"status": "skipped", "reason": "probe_is_opt_in"}, probe_provider_liveness("https://provider.example/health", opener=fail_if_called))

    def test_enabled_probe_returns_structured_health(self):
        result = probe_provider_liveness("https://provider.example/health", enabled=True, opener=lambda request, timeout: _Response())
        self.assertEqual({"status": "healthy", "status_code": 204}, result)

    def test_credential_bearing_endpoint_is_rejected_without_network(self):
        endpoint = "https://token@provider.example/health?api_key=secret"
        self.assertIn("endpoint_must_not_contain_credentials_or_parameters", validate_probe_endpoint(endpoint))
        self.assertEqual("invalid", probe_provider_liveness(endpoint, enabled=True).get("status"))

    def test_timeout_is_bounded(self):
        with self.assertRaises(ValueError):
            probe_provider_liveness("https://provider.example/health", enabled=True, timeout_seconds=11)


if __name__ == "__main__":
    unittest.main()
