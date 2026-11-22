#!/usr/bin/env python3
"""Validate offline evidence that an inference GPU node is release-ready."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys


_IMAGE_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")

REQUIRED_BOOLEAN_FIELDS = (
    "model_cache_ready",
    "health_check_passed",
    "gpu_metrics_available",
    "rollback_ready",
)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def gpu_node_readiness_violations(
    observations: object,
    *,
    now: datetime,
    maximum_age_seconds: int = 900,
    minimum_gpu_count: int = 1,
) -> tuple[str, ...]:
    """Return deterministic violations for collected GPU node readiness evidence."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if (
        not isinstance(maximum_age_seconds, int)
        or isinstance(maximum_age_seconds, bool)
        or maximum_age_seconds <= 0
    ):
        raise ValueError("maximum age must be a positive integer")
    if (
        not isinstance(minimum_gpu_count, int)
        or isinstance(minimum_gpu_count, bool)
        or minimum_gpu_count <= 0
    ):
        raise ValueError("minimum GPU count must be a positive integer")
    if not isinstance(observations, list) or not observations:
        return ("at_least_one_gpu_node_observation_is_required",)

    violations: list[str] = []
    seen_nodes: set[str] = set()
    for index, observation in enumerate(observations):
        prefix = f"node_{index}"
        if not isinstance(observation, dict):
            violations.append(f"{prefix}:observation_must_be_an_object")
            continue

        node = observation.get("node")
        if not isinstance(node, str) or not node.strip():
            violations.append(f"{prefix}:node_is_required")
        elif node in seen_nodes:
            violations.append(f"{prefix}:node_must_be_unique")
        else:
            seen_nodes.add(node)

        for field in ("driver_version", "container_runtime"):
            value = observation.get(field)
            if not isinstance(value, str) or not value.strip():
                violations.append(f"{prefix}:{field}_is_required")

        gpu_count = observation.get("gpu_count")
        if (
            not isinstance(gpu_count, int)
            or isinstance(gpu_count, bool)
            or gpu_count < minimum_gpu_count
        ):
            violations.append(f"{prefix}:gpu_count_is_below_minimum")

        for field in REQUIRED_BOOLEAN_FIELDS:
            if observation.get(field) is not True:
                violations.append(f"{prefix}:{field}_must_be_true")

        model_digest = observation.get("model_image_digest")
        rollback_digest = observation.get("rollback_image_digest")
        if not isinstance(model_digest, str) or not _IMAGE_DIGEST.fullmatch(model_digest):
            violations.append(f"{prefix}:model_image_digest_must_be_immutable")
        if not isinstance(rollback_digest, str) or not _IMAGE_DIGEST.fullmatch(rollback_digest):
            violations.append(f"{prefix}:rollback_image_digest_must_be_immutable")
        if (
            isinstance(model_digest, str)
            and isinstance(rollback_digest, str)
            and _IMAGE_DIGEST.fullmatch(model_digest)
            and _IMAGE_DIGEST.fullmatch(rollback_digest)
            and model_digest == rollback_digest
        ):
            violations.append(f"{prefix}:rollback_image_digest_must_differ")

        observed_at = _timestamp(observation.get("observed_at"))
        if observed_at is None:
            violations.append(f"{prefix}:observed_at_must_be_timezone_aware")
        else:
            age = (now - observed_at).total_seconds()
            if age < 0 or age > maximum_age_seconds:
                violations.append(f"{prefix}:readiness_evidence_is_not_fresh")

    return tuple(violations)


def _load_observations(path: Path) -> object:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("GPU node readiness observations must be a JSON array")
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate GPU node readiness evidence without contacting a GPU or provider."
    )
    parser.add_argument("observations", type=Path, help="JSON GPU node readiness observations")
    parser.add_argument("--now", help="ISO-8601 policy evaluation time; defaults to current UTC time")
    parser.add_argument("--maximum-age-seconds", type=int, default=900)
    parser.add_argument("--minimum-gpu-count", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        observations = _load_observations(args.observations)
        now = datetime.now(timezone.utc) if args.now is None else _timestamp(args.now)
        if now is None:
            raise ValueError("now must be a timezone-aware ISO-8601 timestamp")
        violations = gpu_node_readiness_violations(
            observations,
            now=now,
            maximum_age_seconds=args.maximum_age_seconds,
            minimum_gpu_count=args.minimum_gpu_count,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    report = {
        "maximum_age_seconds": args.maximum_age_seconds,
        "minimum_gpu_count": args.minimum_gpu_count,
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
