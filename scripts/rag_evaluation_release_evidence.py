from __future__ import annotations

from datetime import datetime


_REQUIRED_METRICS = ("groundedness", "answer_relevance")


def evaluation_release_evidence_violations(evidence: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    for field in ("evaluation_id", "dataset_version"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            violations.append(f"{field}_is_required")
    metrics = evidence.get("metrics")
    thresholds = evidence.get("thresholds")
    if not isinstance(metrics, dict):
        violations.append("metrics_must_be_an_object")
    if not isinstance(thresholds, dict):
        violations.append("thresholds_must_be_an_object")
    for metric in _REQUIRED_METRICS:
        observed = metrics.get(metric) if isinstance(metrics, dict) else None
        threshold = thresholds.get(metric) if isinstance(thresholds, dict) else None
        if not _is_probability(observed):
            violations.append(f"{metric}_must_be_a_probability")
        if not _is_probability(threshold):
            violations.append(f"{metric}_threshold_must_be_a_probability")
        elif _is_probability(observed) and observed < threshold:
            violations.append(f"{metric}_is_below_release_threshold")
    if _parse_timestamp(evidence.get("evaluated_at")) is None:
        violations.append("evaluated_at_must_be_timezone_aware")
    if evidence.get("regression_reviewed") is not True:
        violations.append("regression_review_must_pass")
    return tuple(violations)


def evaluation_release_is_ready(evidence: dict[str, object]) -> bool:
    return not evaluation_release_evidence_violations(evidence)


def _is_probability(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
