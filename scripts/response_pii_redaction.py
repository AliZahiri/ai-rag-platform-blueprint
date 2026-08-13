from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from scripts.prompt_redaction_check import detected_sensitive_fields


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def response_pii_redaction_violations(response: str, report: dict[str, object], *, now: datetime, maximum_age_seconds: int = 900) -> tuple[str, ...]:
    if not isinstance(response, str):
        raise ValueError("response must be a string")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_age_seconds, int) or isinstance(maximum_age_seconds, bool) or maximum_age_seconds <= 0:
        raise ValueError("maximum report age must be a positive integer")

    violations: list[str] = []
    expected_digest = sha256(response.encode("utf-8")).hexdigest()
    if report.get("response_sha256") != expected_digest:
        violations.append("response_digest_must_match_content")
    if not isinstance(report.get("detector_version"), str) or not report["detector_version"].strip():
        violations.append("detector_version_is_required")

    scanned_at = _timestamp(report.get("scanned_at"))
    if scanned_at is None:
        violations.append("scanned_at_must_be_timezone_aware")
    else:
        age = (now - scanned_at).total_seconds()
        if age < 0:
            violations.append("scan_time_is_in_the_future")
        elif age > maximum_age_seconds:
            violations.append("scan_is_stale")

    detected = detected_sensitive_fields(response)
    reported_categories = report.get("detected_categories")
    if not isinstance(reported_categories, list) or not all(isinstance(item, str) and item.strip() for item in reported_categories):
        violations.append("detected_categories_must_be_a_string_list")
    elif set(reported_categories) != set(detected):
        violations.append("detected_categories_must_match_response")
    if detected:
        violations.append("response_contains_sensitive_data")
        if report.get("release_decision") != "blocked":
            violations.append("sensitive_response_must_be_blocked")
    elif report.get("release_decision") != "allowed":
        violations.append("clean_response_must_be_explicitly_allowed")
    return tuple(violations)


def response_is_safe_to_release(response: str, report: dict[str, object], **policy: object) -> bool:
    return not response_pii_redaction_violations(response, report, **policy)
