from __future__ import annotations

from datetime import datetime
from math import isfinite


def provider_latency_slo_violations(evidence: dict[str, object], *, minimum_samples: int = 100, maximum_p95_ms: float = 2000.0, maximum_error_rate: float = 0.01) -> tuple[str, ...]:
    if not isinstance(minimum_samples, int) or isinstance(minimum_samples, bool) or minimum_samples < 1:
        raise ValueError("minimum_samples must be a positive integer")
    if not _non_negative_finite(maximum_p95_ms) or maximum_p95_ms == 0:
        raise ValueError("maximum_p95_ms must be positive and finite")
    if not _probability(maximum_error_rate):
        raise ValueError("maximum_error_rate must be a probability")
    violations: list[str] = []
    if not isinstance(evidence.get("provider"), str) or not evidence["provider"].strip():
        violations.append("provider_is_required")
    samples = evidence.get("sample_count")
    if not isinstance(samples, int) or isinstance(samples, bool) or samples < minimum_samples:
        violations.append("sample_count_is_below_minimum")
    percentiles = evidence.get("latency_ms")
    values: dict[str, float] = {}
    if not isinstance(percentiles, dict):
        violations.append("latency_ms_must_be_an_object")
    else:
        for name in ("p50", "p95", "p99"):
            value = percentiles.get(name)
            if not _non_negative_finite(value):
                violations.append(f"latency_{name}_must_be_finite_and_non_negative")
            else:
                values[name] = float(value)
    if len(values) == 3 and not values["p50"] <= values["p95"] <= values["p99"]:
        violations.append("latency_percentiles_must_be_ordered")
    if "p95" in values and values["p95"] > maximum_p95_ms:
        violations.append("provider_p95_latency_exceeds_budget")
    error_rate = evidence.get("error_rate")
    if not _probability(error_rate):
        violations.append("error_rate_must_be_a_probability")
    elif error_rate > maximum_error_rate:
        violations.append("provider_error_rate_exceeds_budget")
    if _timestamp(evidence.get("observed_at")) is None:
        violations.append("observed_at_must_be_timezone_aware")
    return tuple(violations)


def provider_latency_slo_is_met(evidence: dict[str, object], **policy: object) -> bool:
    return not provider_latency_slo_violations(evidence, **policy)


def _non_negative_finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and value >= 0


def _probability(value: object) -> bool:
    return _non_negative_finite(value) and value <= 1


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
