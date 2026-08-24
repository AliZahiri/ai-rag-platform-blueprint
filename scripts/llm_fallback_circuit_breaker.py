from __future__ import annotations

from datetime import datetime


def circuit_breaker_violations(evidence: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    state = evidence.get("state")
    if state not in {"closed", "open", "half_open"}:
        violations.append("state_is_invalid")
    failures, threshold = evidence.get("consecutive_failures"), evidence.get("failure_threshold")
    if not isinstance(failures, int) or isinstance(failures, bool) or failures < 0:
        violations.append("consecutive_failures_must_be_non_negative")
    if not isinstance(threshold, int) or isinstance(threshold, bool) or threshold < 1:
        violations.append("failure_threshold_must_be_positive")
    if state == "open" and isinstance(failures, int) and isinstance(threshold, int) and failures < threshold:
        violations.append("open_state_requires_threshold_failures")
    if state == "open" and _timestamp(evidence.get("retry_at")) is None:
        violations.append("open_state_requires_timezone_aware_retry_at")
    if not isinstance(evidence.get("fallback_route"), str) or not evidence["fallback_route"].strip():
        violations.append("fallback_route_is_required")
    if _timestamp(evidence.get("observed_at")) is None:
        violations.append("observed_at_must_be_timezone_aware")
    return tuple(violations)


def circuit_breaker_is_safe(evidence: dict[str, object]) -> bool:
    return not circuit_breaker_violations(evidence)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
