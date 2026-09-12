#!/usr/bin/env python3
"""Bind offline evidence to an approved scope and artifact revision."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_FIELDS = ("corpus_id","embedding_model","index_sha256",)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def evidence_binding_violations(evidence: object, *, expected: object,
                                now: datetime, maximum_age_seconds: int = 300) -> tuple[str, ...]:
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if type(maximum_age_seconds) is not int or maximum_age_seconds < 1:
        raise ValueError("maximum_age_seconds must be a positive integer")
    if not isinstance(expected, dict) or set(expected) != set(REQUIRED_FIELDS):
        raise ValueError("expected must contain exactly the approved binding fields")
    for field in REQUIRED_FIELDS:
        value = expected[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("approved binding values must be nonempty strings")
        if ("sha256" in field or "digest" in field) and not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
            raise ValueError("approved digests must use sha256:<64 lowercase hex characters>")
    if not isinstance(evidence, dict):
        return ("evidence_must_be_an_object",)
    violations = [f"{field}:binding_mismatch" for field in REQUIRED_FIELDS
                  if evidence.get(field) != expected[field]]
    observed = _timestamp(evidence.get("observed_at"))
    if observed is None or not 0 <= (now - observed).total_seconds() <= maximum_age_seconds:
        violations.append("observation_is_invalid_stale_or_future_dated")
    return tuple(violations)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--now", required=True, help="Timezone-aware ISO 8601 decision time")
    parser.add_argument("--maximum-age-seconds", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be an object")
        now = _timestamp(args.now)
        if now is None:
            raise ValueError("--now must be timezone-aware")
        violations = evidence_binding_violations(manifest.get("evidence"),
            expected=manifest.get("expected"), now=now,
            maximum_age_seconds=args.maximum_age_seconds)
    except (OSError, UnicodeError, ValueError):
        print(json.dumps({"status": "error", "error": "invalid_manifest_or_policy"}, sort_keys=True))
        return 2
    print(json.dumps({"status": "rejected" if violations else "passed",
                      "violations": list(violations)}, sort_keys=True))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
