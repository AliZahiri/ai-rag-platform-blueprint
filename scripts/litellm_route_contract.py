#!/usr/bin/env python3
"""Validate LiteLLM routes and fallback chains against workload contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# The release runner executes this file by path rather than as a module.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.litellm_preflight import load_config, validate_config


def _positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _route_index(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    route_list = config.get("routes", [])
    if not isinstance(route_list, list):
        return {}
    return {
        str(route["alias"]): route
        for route in route_list
        if isinstance(route, dict) and route.get("alias")
    }


def _fallback_chain(alias: str, routes: dict[str, dict[str, Any]]) -> list[str]:
    """Return a deterministic breadth-first route chain without looping forever."""
    chain: list[str] = []
    pending = [alias]
    visited: set[str] = set()
    while pending:
        current = pending.pop(0)
        if current in visited:
            continue
        visited.add(current)
        chain.append(current)
        route = routes.get(current, {})
        fallbacks = route.get("fallbacks", [])
        if isinstance(fallbacks, list):
            pending.extend(str(candidate) for candidate in fallbacks)
    return chain


def _route_violations(
    alias: str,
    route: dict[str, Any],
    *,
    required_capabilities: list[str],
    required_context_tokens: int,
) -> list[str]:
    violations: list[str] = []
    capabilities = route.get("capabilities")
    if not isinstance(capabilities, dict):
        return [f"{alias}: capabilities must be an object"]
    for capability in required_capabilities:
        if capabilities.get(capability) is not True:
            violations.append(f"{alias}: capability {capability} is required")
    context_window = capabilities.get("context_window")
    if (
        not isinstance(context_window, int)
        or isinstance(context_window, bool)
        or context_window < required_context_tokens
    ):
        violations.append(
            f"{alias}: context_window must be at least {required_context_tokens}"
        )
    return violations


def validate_workload_contracts(config: dict[str, Any]) -> list[str]:
    """Validate every declared workload and every route in its fallback chain."""
    workloads = config.get("workloads")
    if not isinstance(workloads, list) or not workloads:
        return ["workloads must be a non-empty list"]

    routes = _route_index(config)
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, workload in enumerate(workloads):
        prefix = f"workloads[{index}]"
        if not isinstance(workload, dict):
            errors.append(f"{prefix} must be an object")
            continue

        workload_id = str(workload.get("id", "")).strip()
        if not workload_id:
            errors.append(f"{prefix}.id is required")
        elif workload_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {workload_id}")
        seen_ids.add(workload_id)

        route_alias = str(workload.get("route", "")).strip()
        if route_alias not in routes:
            errors.append(f"{prefix}: route {route_alias or '<missing>'} is not defined")

        capabilities = workload.get("required_capabilities")
        normalized_capabilities = (
            [item.strip() for item in capabilities]
            if isinstance(capabilities, list)
            and all(isinstance(item, str) and item.strip() for item in capabilities)
            else []
        )
        if (
            not normalized_capabilities
            or len(set(normalized_capabilities)) != len(normalized_capabilities)
        ):
            errors.append(f"{prefix}.required_capabilities must be a non-empty unique list")
            required_capabilities: list[str] = []
        else:
            required_capabilities = normalized_capabilities

        required_context_tokens = workload.get("required_context_tokens")
        if not _positive_integer(required_context_tokens):
            errors.append(f"{prefix}.required_context_tokens must be a positive integer")
            required_context_tokens = 1

        if route_alias not in routes:
            continue
        for candidate in _fallback_chain(route_alias, routes):
            errors.extend(
                _route_violations(
                    candidate,
                    routes[candidate],
                    required_capabilities=required_capabilities,
                    required_context_tokens=required_context_tokens,
                )
            )
    return errors


def validation_report(config: dict[str, Any], errors: list[str]) -> dict[str, object]:
    routes = _route_index(config)
    workloads = config.get("workloads", [])
    if not isinstance(workloads, list):
        workloads = []
    return {
        "errors": errors,
        "ok": not errors,
        "routes": [
            {
                "alias": alias,
                "fallbacks": route.get("fallbacks", []),
                "model": route.get("model", ""),
                "provider": route.get("provider", ""),
            }
            for alias, route in routes.items()
        ],
        "workloads": [
            {
                "id": workload.get("id", ""),
                "route": workload.get("route", ""),
                "fallback_chain": _fallback_chain(str(workload.get("route", "")), routes),
            }
            for workload in workloads
            if isinstance(workload, dict)
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate LiteLLM routes and fallback workload contracts."
    )
    parser.add_argument("--config", default="configs/litellm-routes.example.json")
    parser.add_argument("--require-secrets", action="store_true")
    parser.add_argument("--min-context-window", type=int, default=8192)
    parser.add_argument("--json", dest="json_output", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(Path(args.config))
        errors = validate_config(
            config,
            require_secrets=args.require_secrets,
            min_context_window=args.min_context_window,
        )
        errors.extend(validate_workload_contracts(config))
        report = validation_report(config, errors)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        report = {"errors": [f"unable to load config: {error}"], "ok": False}

    if args.json_output:
        print(json.dumps(report, sort_keys=True))
    elif report["ok"]:
        print("LiteLLM route contract validation passed")
    else:
        for error in report["errors"]:
            print(f"contract-error: {error}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
