#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_LIMITS = ("rpm", "tpm", "max_retries", "timeout_seconds", "cost_cap_usd")
REQUIRED_CAPABILITIES = ("streaming", "tool_calling", "json_mode")
REQUIRED_OBSERVABILITY = ("latency", "tokens", "cost", "failures")
ROUTE_ALIAS_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("LiteLLM preflight config must be a JSON object")
    return data


def route_aliases(routes: list[dict[str, Any]]) -> set[str]:
    return {str(route.get("alias", "")) for route in routes if route.get("alias")}


def validate_route_alias(raw_alias: Any, index: int, aliases: set[str]) -> tuple[str, list[str]]:
    alias = str(raw_alias or "").strip()
    errors: list[str] = []
    if not alias:
        return f"routes[{index}]", [f"routes[{index}]: alias is required"]
    if not ROUTE_ALIAS_PATTERN.fullmatch(alias):
        errors.append(f"{alias}: alias must use lowercase letters, numbers, and hyphens")
    if alias in aliases:
        errors.append(f"{alias}: duplicate route alias")
    return alias, errors


def validate_fallbacks(routes: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    aliases = route_aliases(routes)
    graph: dict[str, list[str]] = {}

    for route in routes:
        alias = str(route.get("alias", ""))
        fallbacks = route.get("fallbacks", [])
        if not isinstance(fallbacks, list):
            errors.append(f"{alias}: fallbacks must be a list")
            continue
        graph[alias] = [str(fallback) for fallback in fallbacks]
        for fallback in graph[alias]:
            if fallback not in aliases:
                errors.append(f"{alias}: fallback {fallback} is not defined as a route alias")

    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(alias: str, path: list[str]) -> None:
        if alias in visiting:
            cycle = " -> ".join([*path, alias])
            errors.append(f"fallback cycle detected: {cycle}")
            return
        if alias in visited:
            return

        visiting.add(alias)
        for fallback in graph.get(alias, []):
            if fallback in graph:
                walk(fallback, [*path, alias])
        visiting.remove(alias)
        visited.add(alias)

    for alias in graph:
        walk(alias, [])

    return errors


def validate_limits(alias: str, limits: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(limits, dict):
        return [f"{alias}: limits must be an object"]
    for key in REQUIRED_LIMITS:
        value = limits.get(key)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or (isinstance(value, float) and not math.isfinite(value))
            or value < 0
        ):
            errors.append(f"{alias}: limits.{key} must be a finite non-negative number")
    if limits.get("rpm", 0) == 0:
        errors.append(f"{alias}: limits.rpm must be greater than zero")
    if limits.get("tpm", 0) == 0:
        errors.append(f"{alias}: limits.tpm must be greater than zero")
    if limits.get("timeout_seconds", 0) == 0:
        errors.append(f"{alias}: limits.timeout_seconds must be greater than zero")
    return errors


def validate_capabilities(alias: str, capabilities: Any, min_context_window: int) -> list[str]:
    errors: list[str] = []
    if not isinstance(capabilities, dict):
        return [f"{alias}: capabilities must be an object"]
    for key in REQUIRED_CAPABILITIES:
        if capabilities.get(key) is not True:
            errors.append(f"{alias}: capabilities.{key} must be true for the RAG route")
    context_window = capabilities.get("context_window")
    if not isinstance(context_window, int) or context_window < min_context_window:
        errors.append(
            f"{alias}: capabilities.context_window must be at least {min_context_window}"
        )
    return errors


def validate_observability(config: dict[str, Any]) -> list[str]:
    observability = config.get("observability", {})
    if not isinstance(observability, dict):
        return ["observability must be an object"]
    return [
        f"observability.{key} must be enabled"
        for key in REQUIRED_OBSERVABILITY
        if observability.get(key) is not True
    ]


def validate_config(
    config: dict[str, Any],
    *,
    require_secrets: bool = False,
    min_context_window: int = 8192,
) -> list[str]:
    errors: list[str] = []
    routes = config.get("routes")
    if not isinstance(routes, list) or not routes:
        return ["routes must be a non-empty list"]

    aliases: set[str] = set()
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            errors.append(f"routes[{index}] must be an object")
            continue
        alias, alias_errors = validate_route_alias(route.get("alias"), index, aliases)
        provider = str(route.get("provider", "")).strip()
        model = str(route.get("model", "")).strip()
        env_key = str(route.get("env_key", "")).strip()

        if alias_errors:
            errors.extend(alias_errors)
        aliases.add(alias)

        if not provider:
            errors.append(f"{alias}: provider is required")
        if not model:
            errors.append(f"{alias}: model is required")
        if not env_key:
            errors.append(f"{alias}: env_key is required")
        elif require_secrets and not os.environ.get(env_key):
            errors.append(f"{alias}: required environment secret {env_key} is missing")

        errors.extend(validate_limits(alias, route.get("limits")))
        errors.extend(validate_capabilities(alias, route.get("capabilities"), min_context_window))

    errors.extend(validate_fallbacks([route for route in routes if isinstance(route, dict)]))
    errors.extend(validate_observability(config))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate LiteLLM route preflight config.")
    parser.add_argument("--config", default="configs/litellm-routes.example.json")
    parser.add_argument("--require-secrets", action="store_true")
    parser.add_argument("--min-context-window", type=int, default=8192)
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print one machine-readable validation report to stdout.",
    )
    parser.add_argument(
        "--live-probe",
        action="store_true",
        help="Reserved for explicit provider liveness probes. No paid calls run by default.",
    )
    return parser.parse_args()


def validation_report(errors: list[str], *, live_probe_requested: bool) -> dict[str, object]:
    return {
        "ok": not errors,
        "errors": errors,
        "live_probe_requested": live_probe_requested,
    }


def main() -> int:
    args = parse_args()
    try:
        config = load_config(Path(args.config))
        errors = validate_config(
            config,
            require_secrets=args.require_secrets,
            min_context_window=args.min_context_window,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        errors = [f"unable to load config: {error}"]

    if args.json_output:
        print(
            json.dumps(
                validation_report(errors, live_probe_requested=args.live_probe),
                sort_keys=True,
            )
        )
    elif args.live_probe:
        print("live probes are opt-in and must be wired per provider; no provider calls were made")

    if errors:
        if not args.json_output:
            for error in errors:
                print(f"preflight-error: {error}", file=sys.stderr)
        return 1

    if not args.json_output:
        print("LiteLLM preflight validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
