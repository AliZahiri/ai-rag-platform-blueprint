from __future__ import annotations

from datetime import datetime
import re


_SHA256 = re.compile(r"(?:sha256:)?[0-9a-f]{64}\Z")


def embedding_model_provenance_violations(evidence: dict[str, object], *, expected_model_id: str, expected_revision: str, expected_dimension: int, expected_index_snapshot: str, now: datetime, maximum_age_seconds: int = 86400) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if any(not isinstance(value, str) or not value.strip() for value in (expected_model_id, expected_revision, expected_index_snapshot)):
        raise ValueError("expected model contract values must be non-empty strings")
    if not isinstance(expected_dimension, int) or isinstance(expected_dimension, bool) or expected_dimension < 1:
        raise ValueError("expected dimension must be a positive integer")
    if not isinstance(maximum_age_seconds, int) or isinstance(maximum_age_seconds, bool) or maximum_age_seconds < 1:
        raise ValueError("maximum evidence age must be a positive integer")

    violations: list[str] = []
    for field, expected in (("model_id", expected_model_id), ("model_revision", expected_revision), ("index_snapshot", expected_index_snapshot)):
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            violations.append(f"{field}_is_required")
        elif value != expected:
            violations.append(f"{field}_does_not_match_expected")
    dimension = evidence.get("embedding_dimension")
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 1:
        violations.append("embedding_dimension_must_be_positive")
    elif dimension != expected_dimension:
        violations.append("embedding_dimension_does_not_match_expected")
    digest = evidence.get("model_sha256")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        violations.append("model_sha256_must_be_a_sha256_digest")
    observed_at = _timestamp(evidence.get("observed_at"))
    if observed_at is None:
        violations.append("observed_at_must_be_timezone_aware")
    elif not 0 <= (now - observed_at).total_seconds() <= maximum_age_seconds:
        violations.append("embedding_provenance_evidence_is_stale_or_future_dated")
    return tuple(violations)


def embedding_model_provenance_is_ready(evidence: dict[str, object], **policy: object) -> bool:
    return not embedding_model_provenance_violations(evidence, **policy)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
