#!/usr/bin/env python3
"""Collect bounded, credential-safe readiness evidence from local platform services."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT_SECONDS = 3.0
MAX_TIMEOUT_SECONDS = 10.0


def validate_endpoint(endpoint: str) -> tuple[str, ...]:
    """Reject endpoints that could embed credentials or request-specific secrets."""
    parsed = urlsplit(endpoint)
    violations: list[str] = []
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        violations.append("http_endpoint_is_required")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        violations.append("endpoint_must_not_contain_credentials_or_parameters")
    return tuple(violations)


def _timestamp(now: Callable[[], datetime]) -> str:
    value = now()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def collect_endpoint_readiness(
    name: str,
    endpoint: str,
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    opener: Callable[..., Any] = urlopen,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    """Return a structured observation without exposing response content or errors."""
    if isinstance(timeout_seconds, bool) or not 0 < timeout_seconds <= MAX_TIMEOUT_SECONDS:
        raise ValueError("timeout must be greater than zero and at most ten seconds")

    checked_at = _timestamp(now)
    violations = validate_endpoint(endpoint)
    if violations:
        return {
            "name": name,
            "status": "invalid",
            "checked_at": checked_at,
            "violations": list(violations),
        }

    request = Request(endpoint, headers={"Accept": "application/json"}, method="GET")
    started_at = monotonic()
    response: Any | None = None
    try:
        response = opener(request, timeout=timeout_seconds)
        status = getattr(response, "status", None)
        status_code = int(status if status is not None else response.getcode())
    except Exception as error:
        return {
            "name": name,
            "status": "unavailable",
            "checked_at": checked_at,
            "error_type": type(error).__name__,
            "latency_ms": round((monotonic() - started_at) * 1000, 3),
        }
    finally:
        if response is not None and hasattr(response, "close"):
            response.close()

    return {
        "name": name,
        "status": "healthy" if 200 <= status_code < 400 else "unhealthy",
        "checked_at": checked_at,
        "status_code": status_code,
        "latency_ms": round((monotonic() - started_at) * 1000, 3),
    }


def collect_platform_readiness(
    endpoints: Sequence[tuple[str, str, bool]],
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    opener: Callable[..., Any] = urlopen,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    """Collect service observations and make the required-service decision explicit."""
    observations = [
        collect_endpoint_readiness(
            name,
            endpoint,
            timeout_seconds=timeout_seconds,
            opener=opener,
            now=now,
            monotonic=monotonic,
        )
        for name, endpoint, _ in endpoints
    ]
    required_observations = [
        observation
        for observation, (_, _, required) in zip(observations, endpoints, strict=True)
        if required
    ]
    failed_required = [
        str(observation["name"])
        for observation in required_observations
        if observation["status"] != "healthy"
    ]
    return {
        "status": "ready" if not failed_required else "degraded",
        "required_services": [name for name, _, required in endpoints if required],
        "failed_required_services": failed_required,
        "observations": observations,
    }


def _health_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect JSON readiness evidence for the local RAG platform services."
    )
    parser.add_argument("--vector-db-url", default="http://localhost:6333")
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--grafana-url", default="http://localhost:3000")
    parser.add_argument(
        "--litellm-url",
        help="Optional LiteLLM base URL; it is only probed when explicitly supplied.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit non-zero when any required service is not healthy.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    endpoints: list[tuple[str, str, bool]] = [
        ("vector-db", _health_url(args.vector_db_url, "/healthz"), True),
        ("prometheus", _health_url(args.prometheus_url, "/-/ready"), True),
        ("grafana", _health_url(args.grafana_url, "/api/health"), True),
    ]
    if args.litellm_url:
        endpoints.append(
            ("litellm", _health_url(args.litellm_url, "/health/liveliness"), True)
        )

    try:
        report = collect_platform_readiness(
            endpoints,
            timeout_seconds=args.timeout_seconds,
        )
    except ValueError as error:
        print(json.dumps({"status": "invalid", "error": str(error)}))
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    if any(observation["status"] == "invalid" for observation in report["observations"]):
        return 2
    return 1 if args.require_ready and report["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
