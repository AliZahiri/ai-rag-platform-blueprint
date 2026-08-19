from __future__ import annotations

from datetime import datetime
from math import isfinite


def _non_negative_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and value >= 0


def cost_anomaly_violations(observation: dict[str, object], policy: dict[str, object], *, now: datetime) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    daily_cap, growth_ratio = policy.get("daily_cap_usd"), policy.get("maximum_growth_ratio")
    if not _non_negative_number(daily_cap) or daily_cap <= 0:
        raise ValueError("daily cap must be a positive finite number")
    if not _non_negative_number(growth_ratio) or growth_ratio < 1:
        raise ValueError("maximum growth ratio must be at least one")
    violations: list[str] = []
    if not isinstance(observation.get("provider"), str) or not observation["provider"].strip():
        violations.append("provider_is_required")
    cost, baseline = observation.get("cost_usd"), observation.get("baseline_cost_usd")
    if not _non_negative_number(cost):
        violations.append("cost_usd_must_be_a_finite_non_negative_number")
    elif float(cost) > float(daily_cap):
        violations.append("cost_usd_exceeds_daily_cap")
    if not _non_negative_number(baseline):
        violations.append("baseline_cost_usd_must_be_a_finite_non_negative_number")
    elif _non_negative_number(cost) and baseline > 0 and float(cost) > float(baseline) * float(growth_ratio):
        violations.append("cost_growth_exceeds_ratio")
    value = observation.get("observed_at")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError:
        timestamp = None
    if timestamp is None or timestamp.tzinfo is None or timestamp.utcoffset() is None:
        violations.append("observed_at_must_be_timezone_aware")
    elif (now - timestamp).total_seconds() < 0:
        violations.append("observed_at_must_not_be_in_the_future")
    return tuple(violations)


def cost_observation_is_within_policy(observation: dict[str, object], policy: dict[str, object], *, now: datetime) -> bool:
    return not cost_anomaly_violations(observation, policy, now=now)
