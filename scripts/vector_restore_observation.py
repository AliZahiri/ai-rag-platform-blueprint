from __future__ import annotations

from datetime import datetime
import re


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def vector_restore_violations(observation: dict[str, object], *, now: datetime, maximum_age_seconds: int = 86400) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_age_seconds, int) or isinstance(maximum_age_seconds, bool) or maximum_age_seconds <= 0:
        raise ValueError("maximum age must be a positive integer")
    violations: list[str] = []
    for field in ("expected_record_count", "restored_record_count", "expected_dimension", "restored_dimension"):
        value = observation.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            violations.append(f"{field}_must_be_a_positive_integer")
    if observation.get("expected_record_count") != observation.get("restored_record_count"):
        violations.append("restored_record_count_mismatch")
    if observation.get("expected_dimension") != observation.get("restored_dimension"):
        violations.append("restored_dimension_mismatch")
    expected = observation.get("expected_manifest_sha256")
    restored = observation.get("restored_manifest_sha256")
    if not isinstance(expected, str) or not _SHA256.fullmatch(expected) or not isinstance(restored, str) or not _SHA256.fullmatch(restored):
        violations.append("manifest_sha256_values_must_be_valid")
    elif expected != restored:
        violations.append("restored_manifest_sha256_mismatch")
    if observation.get("sample_query_passed") is not True:
        violations.append("sample_similarity_query_must_pass")
    try:
        verified = datetime.fromisoformat(str(observation.get("verified_at", "")).replace("Z", "+00:00"))
    except ValueError:
        verified = None
    if verified is None or verified.tzinfo is None or verified.utcoffset() is None:
        violations.append("verified_at_must_be_timezone_aware")
    else:
        age = (now - verified).total_seconds()
        if age < 0 or age > maximum_age_seconds:
            violations.append("restore_verification_is_not_fresh")
    return tuple(violations)
