from __future__ import annotations

from datetime import datetime
import re


_SHA256 = re.compile(r"(?:sha256:)?[0-9a-f]{64}\Z")


def vector_index_build_violations(manifest: dict[str, object], build: dict[str, object], *, now: datetime, maximum_age_seconds: int = 3600) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_age_seconds, int) or isinstance(maximum_age_seconds, bool) or maximum_age_seconds < 1:
        raise ValueError("maximum_age_seconds must be a positive integer")
    violations: list[str] = []
    for field in ("document_count", "chunk_count"):
        expected, indexed = manifest.get(field), build.get(f"indexed_{field}")
        if not isinstance(expected, int) or isinstance(expected, bool) or expected < 1:
            violations.append(f"manifest_{field}_must_be_positive")
        elif indexed != expected:
            violations.append(f"indexed_{field}_does_not_match_manifest")
    failed = build.get("failed_record_count")
    if not isinstance(failed, int) or isinstance(failed, bool) or failed != 0:
        violations.append("failed_record_count_must_be_zero")
    digest = build.get("index_digest")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        violations.append("index_digest_must_be_sha256")
    completed_at = _timestamp(build.get("completed_at"))
    if completed_at is None:
        violations.append("completed_at_must_be_timezone_aware")
    elif not 0 <= (now - completed_at).total_seconds() <= maximum_age_seconds:
        violations.append("index_build_evidence_is_stale_or_future_dated")
    return tuple(violations)


def vector_index_build_is_complete(manifest: dict[str, object], build: dict[str, object], **policy: object) -> bool:
    return not vector_index_build_violations(manifest, build, **policy)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
