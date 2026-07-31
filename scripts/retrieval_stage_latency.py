from __future__ import annotations

from math import isfinite


def retrieval_latency_violations(observations: dict[str, object], *, required_stages: tuple[str, ...], maximum_total_ms: float, stage_budgets_ms: dict[str, float] | None = None) -> tuple[str, ...]:
    if not required_stages or any(not str(stage).strip() for stage in required_stages) or len(set(required_stages)) != len(required_stages):
        raise ValueError("required stages must be unique and non-empty")
    if not isinstance(maximum_total_ms, (int, float)) or isinstance(maximum_total_ms, bool) or not isfinite(float(maximum_total_ms)) or maximum_total_ms <= 0:
        raise ValueError("maximum total latency must be positive and finite")
    budgets = stage_budgets_ms or {}
    if set(budgets) - set(required_stages) or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(float(value)) or value <= 0 for value in budgets.values()):
        raise ValueError("stage budgets must reference required stages and be positive")
    violations: list[str] = []
    if set(observations) - set(required_stages):
        violations.append("unexpected_retrieval_stage_observed")
    total = 0.0
    for stage in required_stages:
        value = observations.get(stage)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(float(value)) or value < 0:
            violations.append(f"stage:{stage}:latency_must_be_finite_and_non_negative")
            continue
        total += float(value)
        if stage in budgets and value > budgets[stage]:
            violations.append(f"stage:{stage}:latency_exceeds_budget")
    if total > maximum_total_ms:
        violations.append("total_retrieval_latency_exceeds_budget")
    return tuple(violations)


def retrieval_latency_is_within_budget(observations: dict[str, object], **policy: object) -> bool:
    return not retrieval_latency_violations(observations, **policy)
