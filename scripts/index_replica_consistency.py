from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys


_SHA256 = re.compile(r"(?:sha256:)?[0-9a-f]{64}\Z")


def index_replica_consistency_violations(
    replicas: list[object],
    *,
    expected_generation: str,
    expected_document_count: int,
    expected_sha256: str,
    now: datetime,
    minimum_replicas: int = 2,
    maximum_age_seconds: int = 900,
) -> tuple[str, ...]:
    if not isinstance(expected_generation, str) or not expected_generation.strip():
        raise ValueError("expected_generation must be non-empty")
    if not isinstance(expected_document_count, int) or isinstance(expected_document_count, bool) or expected_document_count < 0:
        raise ValueError("expected_document_count must be non-negative")
    if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
        raise ValueError("expected_sha256 must be a SHA-256 digest")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(minimum_replicas, int) or isinstance(minimum_replicas, bool) or minimum_replicas < 2:
        raise ValueError("minimum_replicas must be at least two")
    if not isinstance(maximum_age_seconds, int) or isinstance(maximum_age_seconds, bool) or maximum_age_seconds < 1:
        raise ValueError("maximum_age_seconds must be positive")
    if not isinstance(replicas, list) or len(replicas) < minimum_replicas:
        return ("minimum_index_replica_count_not_met",)

    violations: list[str] = []
    replica_ids: set[str] = set()
    for index, replica in enumerate(replicas):
        prefix = f"replica_{index}"
        if not isinstance(replica, dict):
            violations.append(f"{prefix}:must_be_an_object")
            continue
        replica_id = replica.get("replica_id")
        if not isinstance(replica_id, str) or not replica_id.strip() or replica_id in replica_ids:
            violations.append(f"{prefix}:replica_id_must_be_non_empty_and_unique")
        else:
            replica_ids.add(replica_id)
        if replica.get("healthy") is not True:
            violations.append(f"{prefix}:must_be_healthy")
        if replica.get("index_generation") != expected_generation:
            violations.append(f"{prefix}:generation_mismatch")
        if replica.get("document_count") != expected_document_count:
            violations.append(f"{prefix}:document_count_mismatch")
        if replica.get("index_sha256") != expected_sha256:
            violations.append(f"{prefix}:digest_mismatch")
        observed_at = _timestamp(replica.get("observed_at"))
        if observed_at is None or not 0 <= (now - observed_at).total_seconds() <= maximum_age_seconds:
            violations.append(f"{prefix}:observation_is_invalid_stale_or_future_dated")
    return tuple(violations)


def index_replicas_are_consistent(replicas: list[object], **policy: object) -> bool:
    return not index_replica_consistency_violations(replicas, **policy)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate vector index replica consistency evidence."
    )
    parser.add_argument("evidence", type=Path, help="JSON evidence file")
    parser.add_argument("--expected-generation", required=True)
    parser.add_argument("--expected-document-count", required=True, type=int)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument(
        "--now",
        help="ISO-8601 policy evaluation time; defaults to the current UTC time",
    )
    parser.add_argument("--minimum-replicas", type=int, default=2)
    parser.add_argument("--maximum-age-seconds", type=int, default=900)
    return parser.parse_args(argv)


def _load_replicas(path: Path) -> list[object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evidence must be a JSON object")
    replicas = payload.get("replicas")
    if not isinstance(replicas, list):
        raise ValueError("evidence.replicas must be a JSON array")
    return replicas


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        replicas = _load_replicas(args.evidence)
        now = datetime.now(timezone.utc) if args.now is None else _timestamp(args.now)
        if now is None:
            raise ValueError("now must be a timezone-aware ISO-8601 timestamp")
        violations = index_replica_consistency_violations(
            replicas,
            expected_generation=args.expected_generation,
            expected_document_count=args.expected_document_count,
            expected_sha256=args.expected_sha256,
            now=now,
            minimum_replicas=args.minimum_replicas,
            maximum_age_seconds=args.maximum_age_seconds,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "status": "error"}), file=sys.stderr)
        return 2

    report = {
        "expected_document_count": args.expected_document_count,
        "expected_generation": args.expected_generation,
        "minimum_replicas": args.minimum_replicas,
        "replica_count": len(replicas),
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
