from __future__ import annotations

from datetime import datetime
from math import isfinite


def evaluation_confidence_violations(evidence: dict[str, object], *, min_samples: int = 100, min_lower_bound: float = 0.8) -> tuple[str, ...]:
    if not isinstance(min_samples, int) or isinstance(min_samples, bool) or min_samples < 1:
        raise ValueError("min_samples must be a positive integer")
    if not _probability(min_lower_bound):
        raise ValueError("min_lower_bound must be a probability")
    violations: list[str] = []
    if not isinstance(evidence.get("dataset_version"), str) or not evidence["dataset_version"].strip():
        violations.append("dataset_version_is_required")
    sample_count = evidence.get("sample_count")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count < min_samples:
        violations.append("sample_count_is_below_minimum")
    if not _probability(evidence.get("confidence_level")) or evidence["confidence_level"] <= 0:
        violations.append("confidence_level_must_be_a_positive_probability")
    lower_bound = evidence.get("score_lower_bound")
    if not _probability(lower_bound):
        violations.append("score_lower_bound_must_be_a_probability")
    elif lower_bound < min_lower_bound:
        violations.append("score_lower_bound_is_below_release_threshold")
    if _timestamp(evidence.get("evaluated_at")) is None:
        violations.append("evaluated_at_must_be_timezone_aware")
    return tuple(violations)


def evaluation_confidence_is_sufficient(evidence: dict[str, object], **policy: object) -> bool:
    return not evaluation_confidence_violations(evidence, **policy)


def _probability(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and 0 <= value <= 1


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
