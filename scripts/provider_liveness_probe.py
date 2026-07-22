from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def validate_probe_endpoint(endpoint: str) -> tuple[str, ...]:
    parsed = urlsplit(endpoint)
    violations: list[str] = []
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        violations.append("http_endpoint_is_required")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        violations.append("endpoint_must_not_contain_credentials_or_parameters")
    return tuple(violations)


def probe_provider_liveness(endpoint: str, *, enabled: bool = False, timeout_seconds: float = 2.0, opener: Callable[..., object] = urlopen) -> dict[str, object]:
    if not enabled:
        return {"status": "skipped", "reason": "probe_is_opt_in"}
    violations = validate_probe_endpoint(endpoint)
    if violations:
        return {"status": "invalid", "violations": violations}
    if isinstance(timeout_seconds, bool) or not 0 < timeout_seconds <= 10:
        raise ValueError("timeout must be greater than zero and at most ten seconds")
    request = Request(endpoint, method="HEAD")
    try:
        response = opener(request, timeout=timeout_seconds)
        status_code = int(getattr(response, "status", 0))
    except Exception as error:
        return {"status": "unavailable", "error_type": type(error).__name__}
    return {"status": "healthy" if 200 <= status_code < 400 else "unhealthy", "status_code": status_code}
