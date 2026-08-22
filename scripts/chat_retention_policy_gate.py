#!/usr/bin/env python3
"""Offline release gate for chat-history retention policies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from chat_retention_policy import (
    missing_retention_fields,
    retention_policy_is_reviewable,
    retention_policy_warnings,
)


def load_policy(path: Path) -> dict[str, Any]:
    """Load a policy document, rejecting JSON values that are not objects."""
    with path.open(encoding="utf-8") as handle:
        policy = json.load(handle)
    if not isinstance(policy, dict):
        raise ValueError("retention policy must be a JSON object")
    return policy


def validation_report(policy: dict[str, object]) -> dict[str, object]:
    """Return a stable, machine-readable report without changing the policy."""
    missing = missing_retention_fields(policy)
    warnings = retention_policy_warnings(policy)
    return {
        "ok": retention_policy_is_reviewable(policy),
        "missing_fields": list(missing),
        "warnings": list(warnings),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a chat-history retention policy without calling external services."
    )
    parser.add_argument("policy", help="Path to the JSON retention policy.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = validation_report(load_policy(Path(args.policy)))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        report: dict[str, object] = {
            "ok": False,
            "missing_fields": [],
            "warnings": [f"unable_to_load_policy: {error}"],
        }

    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
